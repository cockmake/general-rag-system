import asyncio
import io
import json
import logging
import os
import traceback

from aio_pika.abc import AbstractIncomingMessage
from langchain_core.documents import Document

import utils
from milvus_utils import MilvusClientManager
from minio_utils import minio_client
from mq.connection import rabbit_async_client
from utils import get_embedding_instance

# Configure logging
logger = logging.getLogger(__name__)


class DocumentEmbeddingConsumer:
    async def error_message_sender(self, document_id: int, error_msg: str):
        response_message = {
            "documentId": document_id,
            "status": "failed",
            "message": error_msg
        }
        await rabbit_async_client.publish(
            exchange_name="server.interact.llm.exchange",
            routing_key="rag.document.complete.key",
            message=response_message
        )

    async def on_receive_message(self, message: AbstractIncomingMessage):
        async with message.process():
            try:
                body = message.body.decode()
                logger.info(f"Received document processing task: {body}")
                data = json.loads(body)

                document_id = data.get("documentId")
                kb_id = data.get("kbId")
                user_id = data.get("userId")
                file_path = data.get("filePath")
                file_name = data.get("fileName")
                bucket_name = data.get("bucketName")

                # Download file
                response = await minio_client.get_object(bucket_name, file_path)
                if not response:
                    raise Exception("Failed to download file from MinIO")

                tmp_path = os.path.join('./temp', file_path)
                parent_dir = os.path.dirname(tmp_path)
                if not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)

                suffix = os.path.splitext(file_path)[1]

                minio_byte = await response.read()

                # Only write to disk if not an image (images processed in-memory)
                is_image = suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
                if not is_image:
                    def write_temp_file():
                        with open(tmp_path, "wb") as f:
                            f.write(minio_byte)

                    await asyncio.to_thread(write_temp_file)

                vector_store = None
                try:
                    if suffix.lower() == ".pdf":
                        # chunk_overlap=0 可确保不重复
                        texts = await utils.pdf_split(tmp_path)
                        splits = [Document(page_content=t) for t in texts]
                    elif suffix.lower() == ".txt":
                        def split_txt():
                            with open(tmp_path, "r", encoding="utf-8") as f:
                                return [Document(page_content=t) for t in utils.plain_text_split(f.read())]

                        splits = await asyncio.to_thread(split_txt)
                    elif suffix.lower() == ".md":
                        with open(tmp_path, "r", encoding="utf-8") as f:
                            splits = await asyncio.to_thread(utils.markdown_split, f.read())
                    elif suffix.lower() == ".json":
                        def split_json():
                            with open(tmp_path, "r", encoding="utf-8") as f:
                                json_data = json.load(f)
                                return [Document(page_content=json.dumps(item)) for item in utils.json_split(json_data)]

                        splits = await asyncio.to_thread(split_json)
                    elif suffix.lower() in [".py", ".java", ".js", ".ts", ".vue", ".html", ".rb"]:
                        def split_code(lang):
                            with open(tmp_path, "r", encoding="utf-8") as f:
                                return [Document(page_content=t) for t in utils.code_split(f.read(), lang)]

                        lang_map = {
                            ".py": "python", ".java": "java", ".js": "js", ".ts": "js", ".vue": "js",
                            ".html": "html", ".rb": "ruby"
                        }
                        splits = await asyncio.to_thread(split_code, lang_map[suffix.lower()])
                    elif suffix.lower() in [".xml", ".yml", ".yaml", ".sh", ".css", ".scss"]:
                        def split_plain():
                            with open(tmp_path, "r", encoding="utf-8") as f:
                                return [Document(page_content=t) for t in utils.plain_text_split(f.read())]

                        splits = await asyncio.to_thread(split_plain)
                    elif suffix.lower() in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
                        # Process image directly from bytes
                        splits = await utils.image_split(io.BytesIO(minio_byte))
                    else:
                        logger.warning(f"Unsupported file type: {suffix}")
                        return

                    logger.info(f"Document {document_id} split into {len(splits)} chunks.")
                    for i, doc in enumerate(splits):
                        doc.metadata["documentId"] = document_id
                        doc.metadata["chunkIndex"] = i
                        doc.metadata["fileName"] = file_name
                    # Embed and store
                    milvus_uri = os.environ.get("MILVUS_URI")
                    milvus_token = os.environ.get("MILVUS_TOKEN")
                    # Create vector store
                    embedding_config = {
                        'name': 'text-embedding-v4',
                        'provider': 'qwen'
                    }
                    embeddings = get_embedding_instance(embedding_config)
                    vector_store = await MilvusClientManager.get_instance(
                        user_id, kb_id, milvus_uri, milvus_token, embeddings
                    )
                    max_batch = 10

                    def store_documents_batch():
                        all_ids = []
                        for i in range(0, len(splits), max_batch):
                            batch_ids = vector_store.add_documents(
                                splits[i:i + max_batch]
                            )
                            all_ids.extend(batch_ids)
                        return all_ids

                    ids = await asyncio.to_thread(store_documents_batch)

                    logger.info(f"Document {document_id} processed and stored with {len(ids)} chunks.")
                    chunks_data = []
                    for i, (doc, vector_id) in enumerate(zip(splits, ids)):
                        chunks_data.append({
                            "chunkIndex": i,
                            "text": doc.page_content,
                            "tokenLength": len(doc.page_content),
                            "vectorId": str(vector_id),
                            "metadata": {}
                        })
                    # Send success message
                    response_message = {
                        "documentId": document_id,
                        "status": "success",
                        "message": "Document processed successfully",
                        "chunksCount": len(splits),
                        "chunks": chunks_data
                    }
                    await rabbit_async_client.publish(
                        exchange_name="server.interact.llm.exchange",
                        routing_key="rag.document.complete.key",
                        message=response_message
                    )
                except Exception as e:
                    logger.error(f"Error during embedding or storage: {e}")
                    error_stack = traceback.format_exc()
                    logger.error(error_stack)
                    await self.error_message_sender(document_id, str(e))
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
            except Exception as e:
                logger.error(f"Error processing document: {e}")
                error_stack = traceback.format_exc()
                logger.error(error_stack)
                await self.error_message_sender(document_id, str(e))


document_embedding_consumer = DocumentEmbeddingConsumer()
