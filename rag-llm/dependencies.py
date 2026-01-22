import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from milvus_utils import MilvusClientManager
from mq.connection import rabbit_async_client
from mq.document_embedding import document_embedding_consumer
from mq.session_name import session_name_generator

logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    logger.info("初始化进程")
    logger.info("Initializing RabbitMQ client and consumer...")
    consume_background_tasks = []
    
    # 手动连接而不是使用 async with，避免过早关闭连接
    await rabbit_async_client.connect()
    
    try:
        # 生成 session name
        consume_background_tasks.append(
            asyncio.create_task(
                rabbit_async_client.consume(
                    queue_name="session.name.generate.producer.queue",
                    callback=session_name_generator.on_receive_message
                )
            )
        )
        # 文档向量化
        consume_background_tasks.append(
            asyncio.create_task(
                rabbit_async_client.consume(
                    queue_name="rag.document.process.queue",
                    callback=document_embedding_consumer.on_receive_message
                )
            )
        )
        yield
    finally:
        logger.info("进程结束")
        logger.info("Shutting down RabbitMQ client and consumer...")
        # 先取消任务
        for task in consume_background_tasks:
            task.cancel()
        # 等待任务完成取消
        await asyncio.gather(*consume_background_tasks, return_exceptions=True)
        
        # 关闭 Milvus 连接池
        logger.info("Closing Milvus connections...")
        await MilvusClientManager.close_all()
        
        # 最后关闭连接
        await rabbit_async_client.close()
