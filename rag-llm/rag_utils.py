"""
RAG Service - 多角度查询与并行处理的异步RAG服务
封装了以下高级特性：
1. 多角度查询生成(Multi-Query Generation)
2. 并行检索(Parallel Retrieval)
3. Rerank文档重排序(Document Reranking)
4. 对话历史管理（最近5轮）
5. 流式答案生成
"""
import asyncio
import logging
import os
from typing import AsyncGenerator, Optional

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage
from langchain_milvus import Milvus
from pydantic import BaseModel, Field

from aiohttp_utils import rerank
from utils import get_llm_instance, get_embedding_instance, get_structured_data_instance

logger = logging.getLogger(__name__)


# ============= Pydantic Models =============
class MultiQueryList(BaseModel):
    """多角度查询列表"""
    queries: list[str] = Field(description="从不同角度生成的查询列表")
    grade_query: str = Field(description="用于文档评分的查询，应该是结合上下文、解决指代消歧后的完整问题")
    reasoning: str = Field(description="生成这些查询的原因")


class RAGService:
    """异步RAG服务类"""

    async def generate_multi_queries(
            self,
            question: str,
            history: list,
            model_info: dict
    ) -> tuple[list[str], str]:
        """
        生成多角度查询
        
        Args:
            question: 当前用户问题
            history: 对话历史（LangChain消息格式）
            model_info: 模型配置信息
            
        Returns:
            (多角度查询列表, 评分用查询)
        """
        # 构建对话历史（最近5轮，即10条消息）
        history_context = ""
        if history:
            recent_history = history[-10:] if len(history) > 10 else history
            history_context = "\n".join([
                f"{'用户' if isinstance(m, HumanMessage) else '助手'}: {m.content}"
                for m in recent_history
            ])

        system_prompt = f"""你是一个查询优化专家。你的任务是根据用户的问题，从不同角度生成4-6个查询，涵盖中英文，以便全面检索相关信息。

生成策略：
1. 理解问题的核心意图，结合对话历史解析代词和上下文
2. 提取问题中的关键实体、专业术语、错误码或具体名称，保留在查询中以利于关键词匹配
3. 从不同语义角度拆解问题（如：定义、应用、对比、原理等）
4. 生成的查询应该互补，覆盖问题的不同方面
5. 查询应简洁明确，兼顾向量检索（语义）和关键词检索（精确），多个关键词间请用空格分隔

另外，请额外生成一个'grade_query'，它是对用户当前问题的完整重写（指代消歧后），用于后续的文档相关性评分。
例如：如果用户说“继续”，grade_query 应该是上一轮话题的延续描述，如"关于XXX的进一步详细说明"。

{'对话历史：\n' + history_context if history_context else '无对话历史'}

当前问题：{question}

请生成3-5个不同角度的查询，以及一个grade_query。"""

        llm = get_llm_instance(model_info)
        structured_agent = get_structured_data_instance(llm, MultiQueryList)
        # 使用异步调用
        result = await structured_agent.ainvoke({"messages": [{"role": "user", "content": system_prompt}]})

        logger.info(f"生成的多角度查询: {result['structured_response'].queries}")
        logger.info(f"生成的评分查询(grade_query): {result['structured_response'].grade_query}")
        return result['structured_response'].queries, result['structured_response'].grade_query

    async def parallel_retrieve(
            self,
            query_list: list[str],
            user_id: int,
            kb_id: int,
            top_k: int = 5
    ) -> list[Document]:
        """
        并行检索多个查询
        
        Args:
            query_list: 查询列表
            user_id: 用户ID
            kb_id: 知识库ID
            top_k: 每个查询返回的文档数量
            
        Returns:
            去重后的文档列表
        """
        milvus_uri = os.environ.get("MILVUS_URI")
        milvus_token = os.environ.get("MILVUS_TOKEN")
        db_name = f"group_{user_id // 10000}"
        collection_name = f"kb_{kb_id}"

        embedding_config = {
            'name': 'text-embedding-v4',
            'provider': 'qwen'
        }
        embeddings = get_embedding_instance(embedding_config)

        all_docs = []
        doc_set = set()

        def connect_milvus():
            try:
                return Milvus(
                    embedding_function=embeddings,
                    connection_args={
                        "uri": milvus_uri,
                        "token": milvus_token,
                        "db_name": db_name,
                    },
                    collection_name=collection_name,
                    auto_id=True,
                )
            except Exception as e:
                logger.error(f"连接 Milvus 失败: {e}")
                return None

        vector_store = None
        try:
            vector_store = connect_milvus()
            if not vector_store:
                logger.warning(f"无法连接到知识库: {kb_id}")
                return []

            # 1. 向量检索器 (大幅提高Top-K以增加候选集)
            retriever = vector_store.as_retriever(search_kwargs={"k": top_k})

            # 定义单个查询的异步检索函数（向量检索）
            async def retrieve_vector(query: str) -> list[Document]:
                try:
                    return await retriever.ainvoke(query)
                except Exception as e:
                    logger.error(f"向量检索出错: {e}")
                    return []

            # 定义关键词检索函数（基于Milvus scalar filtering）
            async def retrieve_keyword(query: str) -> list[Document]:
                """
                使用 text like '%keyword%' 进行模糊匹配
                注意：Milvus 的 like 性能较差，仅适合短关键词或作为辅助召回
                """
                # 简单的关键词提取策略：如果查询较短，直接用；否则按空格切分取最长的词
                keywords = []
                if len(query) < 10:
                    keywords.append(query)
                else:
                    # 简单分词，取长度大于2的词
                    words = [w for w in query.split() if len(w) >= 2]
                    keywords.extend(words)
                if not keywords:
                    return []

                docs = []
                try:
                    # 获取集合对象
                    # langchain_milvus.Milvus 实例通常有 col 或 collection 属性
                    col = getattr(vector_store, "col", getattr(vector_store, "collection", None))
                    if not col:
                        logger.error("无法获取 Milvus 集合对象")
                        return []

                    for kw in keywords:
                        # 转义特殊字符
                        safe_kw = kw.replace("'", "\\'").replace('"', '\\"')
                        # 构造表达式: text 字段包含关键词 或 fileName 包含关键词
                        # 注意：字段名默认为 'text'，如果 schema 不同需调整
                        expr = f'text like "%{safe_kw}%" or fileName like "%{safe_kw}%"'

                        # 使用 run_in_executor 避免阻塞
                        res = await asyncio.get_running_loop().run_in_executor(
                            None,
                            lambda: col.query(
                                expr=expr,
                                output_fields=["text", "pk", "documentId", "chunkIndex", "fileName"],  # 确保获取必要字段
                                limit=5  # 限制关键词召回数量，避免过多
                            )
                        )

                        # 转换为 Document 对象
                        for item in res:
                            content = item.pop('text', '')
                            # 移除 milvus 内部字段
                            if 'pk' in item:
                                pk = item['pk']
                            else:
                                pk = str(item.get('id', ''))

                            docs.append(Document(
                                page_content=content,
                                metadata={**item, 'pk': pk, 'retrieval_source': 'keyword'}
                            ))

                except Exception as e:
                    # 关键词检索失败不影响主流程
                    logger.warning(f"关键词检索失败: {e}")

                return docs

            # 并行执行所有检索任务
            tasks = []
            for query in query_list:
                tasks.append(retrieve_vector(query))
                # 对每个查询也尝试关键词检索
                tasks.append(retrieve_keyword(query))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 统计不同来源的文档数量
            count_vector = 0
            count_keyword = 0

            vector_docs = []
            keyword_docs = []

            # 分类收集
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"检索任务失败: {result}")
                    continue
                for doc in result:
                    source = doc.metadata.get('retrieval_source', 'vector')
                    if source == 'keyword':
                        keyword_docs.append(doc)
                    else:
                        vector_docs.append(doc)

            # 优先处理向量检索结果
            for doc in vector_docs:
                pk = doc.metadata.get('pk') or doc.metadata.get('id')
                if pk:
                    pk = str(pk)
                    if pk not in doc_set:
                        doc_set.add(pk)
                        all_docs.append(doc)
                        count_vector += 1

            # 再处理关键词检索结果（补充）
            for doc in keyword_docs:
                pk = doc.metadata.get('pk') or doc.metadata.get('id')
                if pk:
                    pk = str(pk)
                    if pk not in doc_set:
                        doc_set.add(pk)
                        all_docs.append(doc)
                        count_keyword += 1

            logger.info(f"最终去重后共 {len(all_docs)} 个文档 (向量召回: {count_vector}, 关键词召回: {count_keyword})")

        finally:
            # 清理连接
            if vector_store:
                try:
                    await vector_store.aclient.close()
                except Exception:
                    pass

        return all_docs

    async def parallel_grade_documents(
            self,
            documents: list[Document],
            query: str,
            model_info: dict = None,
            top_n: int = 5,
            score_threshold: float = 0.3
    ) -> list[Document]:
        """
        使用Rerank模型评估文档相关性（替代LLM评分）
        
        Args:
            documents: 文档列表
            query: 原始查询
            model_info: 模型配置信息（保留参数以兼容旧接口，但不使用）
            top_n: 返回前N个最相关的文档，默认5个
            score_threshold: 相关性分数阈值（斩杀线），默认0.3，低于此分数的文档将被过滤
            
        Returns:
            按相关性分数排序的文档列表
        """
        if not documents:
            return []

        try:
            # 提取文档内容
            doc_contents = [doc.page_content for doc in documents]

            # 使用rerank进行文档排序，应用斩杀线
            rerank_result = await rerank(
                query=query,
                documents=doc_contents,
                top_n=min(top_n, len(documents)),
                return_documents=False,  # 不需要返回文档内容，节省带宽
                score_threshold=score_threshold  # 应用斩杀线
            )

            # 根据rerank结果重新排序文档
            ranked_docs = []
            for item in rerank_result.get("output", {}).get("results", []):
                original_idx = item['index']
                relevance_score = item['relevance_score']

                # 获取原始文档并添加rerank分数到metadata
                doc = documents[original_idx]
                doc.metadata['rerank_score'] = relevance_score
                ranked_docs.append(doc)

            logger.info(f"Rerank评分完成，返回 {len(ranked_docs)} 个相关文档（斩杀线: {score_threshold}）")
            return ranked_docs

        except Exception as e:
            logger.error(f"Rerank评分失败: {e}，回退到返回所有文档")
            # 出错时返回原始文档列表（兜底策略）
            return documents[:top_n] if len(documents) > top_n else documents

    def merge_consecutive_chunks(self, docs: list[Document]) -> list[Document]:
        """合并同一文档的连续切片，去除重叠部分"""
        if not docs:
            return []

        # 按documentId分组
        docs_by_id = {}
        for doc in docs:
            # 优先使用 metadata 中的 documentId，如果没有则跳过
            doc_id = doc.metadata.get('documentId')
            if doc_id not in docs_by_id:
                docs_by_id[doc_id] = []
            docs_by_id[doc_id].append(doc)

        merged_results = []

        # 对每组进行排序和合并
        for doc_id, group in docs_by_id.items():
            # 区分有chunkIndex和无chunkIndex的文档
            group_with_index = []
            group_without_index = []
            for doc in group:
                if 'chunkIndex' in doc.metadata and doc.metadata['chunkIndex'] is not None:
                    group_with_index.append(doc)
                else:
                    group_without_index.append(doc)
            
            # 无chunkIndex的直接加入结果
            merged_results.extend(group_without_index)
            
            if not group_with_index:
                continue

            # 按 chunkIndex 排序
            group_with_index.sort(key=lambda x: x.metadata.get('chunkIndex'))

            current_merged_doc = group_with_index[0]
            # 初始化 last_chunk_index
            current_merged_doc.metadata['last_chunk_index'] = current_merged_doc.metadata.get('chunkIndex')

            for i in range(1, len(group_with_index)):
                next_doc = group_with_index[i]
                
                last_chunk_idx = current_merged_doc.metadata.get('last_chunk_index')
                curr_chunk_idx = next_doc.metadata.get('chunkIndex')

                if last_chunk_idx is not None and curr_chunk_idx is not None and curr_chunk_idx == last_chunk_idx + 1:
                    # 连续切片，进行合并
                    text1 = current_merged_doc.page_content
                    text2 = next_doc.page_content

                    # 尝试去除重叠
                    # 寻找 text1 的后缀与 text2 的前缀的最长匹配
                    overlap_found = False
                    # 限制最大检测长度，提高性能，通常重叠在 100-200 字符
                    max_overlap_check = min(len(text1), len(text2), 500)
                    min_overlap = 10

                    if max_overlap_check >= min_overlap:
                        # 优化算法：使用 find 替代枚举
                        # 取 text2 的前缀作为种子（长度为 min_overlap）
                        seed = text2[:min_overlap]
                        
                        # 在 text1 的末尾区域搜索种子
                        # 搜索范围从 len(text1) - max_overlap_check 开始
                        start_search = len(text1) - max_overlap_check
                        search_region = text1[start_search:]
                        
                        # 在区域内查找种子
                        pos = search_region.find(seed)
                        while pos != -1:
                            # 计算在 text1 中的绝对位置
                            abs_pos = start_search + pos
                            # 潜在的重叠部分是 text1[abs_pos:]
                            # 检查 text2 是否以这段文本开头
                            potential_overlap = text1[abs_pos:]
                            if text2.startswith(potential_overlap):
                                current_merged_doc.page_content = text1 + text2[len(potential_overlap):]
                                overlap_found = True
                                break
                            # 继续查找下一个匹配
                            pos = search_region.find(seed, pos + 1)

                    if not overlap_found:
                        current_merged_doc.page_content = text1 + text2 # 直接拼接

                    # 更新元数据
                    current_merged_doc.metadata['last_chunk_index'] = curr_chunk_idx
                    # 更新分数为两者的最大值
                    current_merged_doc.metadata['rerank_score'] = max(current_merged_doc.metadata.get('rerank_score', 0), next_doc.metadata.get('rerank_score', 0))

                else:
                    # 不连续，保存当前，开始新的
                    merged_results.append(current_merged_doc)
                    current_merged_doc = next_doc
                    current_merged_doc.metadata['last_chunk_index'] = current_merged_doc.metadata.get('chunkIndex')

            merged_results.append(current_merged_doc)

        # 重新按 rerank_score 排序
        merged_results.sort(key=lambda x: x.metadata.get('rerank_score', 0), reverse=True)

        return merged_results

    async def stream_rag_response_with_process(
            self,
            question: str,
            history: list,
            model_info: dict,
            kb_id: Optional[int] = None,
            user_id: Optional[int] = None,
            system_prompt: Optional[str] = None,
            top_k: int = 15,

            grade_top_n: int = 50,

            grade_score_threshold: float = 0.35,

            top_n: int = 10,
    ) -> AsyncGenerator[dict, None]:
        """
        带过程信息的流式RAG响应生成器
        
        Args:
            question: 用户问题
            history: 对话历史（LangChain消息格式）
            model_info: 模型配置信息
            kb_id: 知识库ID（可选）
            user_id: 用户ID（可选）
            system_prompt: 自定义系统提示词（可选）
            top_k: 每个查询检索的文档数量
            top_n: Rerank后返回的文档数量
            grade_top_n: Rerank评分时考虑的文档数量
            grade_score_threshold: Rerank相关性分数阈值
            
        Yields:
            包含type和payload的字典，type可以是"process"或"content"
        """
        context = "无相关文档"

        # 如果有知识库，执行RAG流程
        if kb_id and user_id:
            try:
                # 1. 生成多角度查询
                yield {
                    "type": "process",
                    "payload": {
                        "step": "query_generation",
                        "title": "生成多角度查询",
                        "description": "正在分析问题并生成多个检索角度...",
                        "status": "running"
                    }
                }

                logger.info("开始生成多角度查询...")
                query_list, grade_query = await self.generate_multi_queries(question, history, model_info)

                yield {
                    "type": "process",
                    "payload": {
                        "step": "query_generation",
                        "title": "生成多角度查询",
                        "description": f"已生成 {len(query_list)} 个检索查询",
                        "status": "completed",
                        "content": "\n".join(
                            [f"- {q}" for q in query_list] + [f"\n**评分查询: ** {grade_query}"])
                    }
                }

                # 2. 并行检索
                yield {
                    "type": "process",
                    "payload": {
                        "step": "retrieval",
                        "title": "检索知识库",
                        "description": "正在从知识库中并行检索相关文档...",
                        "status": "running"
                    }
                }

                logger.info("开始并行检索...")
                all_docs = await self.parallel_retrieve(query_list, user_id, kb_id, top_k=top_k)

                yield {
                    "type": "process",
                    "payload": {
                        "step": "retrieval",
                        "title": "检索知识库",
                        "description": f"检索到 {len(all_docs)} 个候选文档",
                        "status": "completed"
                    }
                }

                # 3. Rerank文档重排序
                graded_docs = []
                if all_docs:
                    yield {
                        "type": "process",
                        "payload": {
                            "step": "rerank",
                            "title": "评估文档相关性",
                            "description": "正在使用Rerank模型评分并排序文档...",
                            "status": "running"
                        }
                    }

                    logger.info("开始Rerank文档重排序...")
                    # 这里的 top_n 传入较大值 (如 50)，以便获取更多候选文档用于后续拼接，
                    # 避免因过早截断导致连续切片丢失。最终的 top_n 截断放在拼接之后。
                    graded_docs = await self.parallel_grade_documents(
                        all_docs,
                        grade_query,
                        top_n=grade_top_n,
                        score_threshold=grade_score_threshold
                    )

                yield {
                    "type": "process",
                    "payload": {
                        "step": "rerank",
                        "title": "评估文档相关性",
                        "description": f"筛选出 {len(graded_docs)} 个相关文档",
                        "status": "completed"
                    }
                }

                # 4. 构建上下文
                merged_docs = []
                if graded_docs:
                    # 合并同一文档的连续切片（在 top_n 截断前进行，以保证完整性）
                    merged_docs = self.merge_consecutive_chunks(graded_docs)

                    # 最终应用 top_n 限制
                    merged_docs = merged_docs[:top_n]

                    context = "\n\n".join([f"[文档{i + 1}]: {doc.page_content}" for i, doc in enumerate(merged_docs)])

                yield {
                    "type": "process",
                    "payload": {
                        "step": "reformat",
                        "title": "构建上下文",
                        "description": f"基于检索和评分结果构建回答上下文，共 {len(merged_docs)} 个文档",
                        "status": "completed",
                        "content": "\n\n---\n\n".join(
                            [f"[相关性：{doc.metadata["rerank_score"]:.3f}][文档{i + 1}]: {doc.page_content}"
                             for i, doc in enumerate(merged_docs)]) if merged_docs else "无相关文档"
                    }
                }


            except Exception as e:
                logger.error(f"RAG流程出错: {e}")
                yield {
                    "type": "process",
                    "payload": {
                        "step": "error",
                        "title": "检索失败",
                        "description": f"检索过程出错: {str(e)}",
                        "status": "error"
                    }
                }
                context = f"检索过程出错: {str(e)}"

        # 5. 生成答案
        yield {
            "type": "process",
            "payload": {
                "step": "generation",
                "title": "生成答案",
                "description": "正在基于检索结果生成回答...",
                "status": "running"
            }
        }

        # 构建系统提示词
        if system_prompt:
            logger.info("使用自定义提示词")
            final_system_prompt = f"""{system_prompt}
m
参考文档：
{context}"""
        else:
            logger.info("使用系统内置提示词")
            final_system_prompt = f"""你是一个专业的AI助手。基于提供的文档和对话历史回答用户问题。

要求：
1. 优先使用提供的文档中的信息
2. 如果文档不足以完整回答，结合对话历史进行推理或明确说明
3. 保持对话连贯，考虑历史上下文
4. 用清晰、简洁的语言回答

参考文档：
{context}"""

        # 构建对话消息
        conversation = [{"role": "system", "content": final_system_prompt}]

        # 添加历史对话（最近5轮）
        recent_history = history[-10:] if len(history) > 10 else history
        for msg in recent_history:
            if isinstance(msg, HumanMessage):
                conversation.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                conversation.append({"role": "assistant", "content": msg.content})

        # 添加当前问题
        conversation.append({"role": "user", "content": question})

        # 获取LLM实例并流式生成
        llm = get_llm_instance(model_info)

        # 使用异步流式生成
        async for chunk in llm.astream(conversation):
            content = chunk.content
            if content:
                yield {
                    "type": "content",
                    "payload": content
                }


# 全局RAG服务实例
rag_service = RAGService()
