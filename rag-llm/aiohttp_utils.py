import asyncio
import logging
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)

EMBEDDING_RERANK_BASE_URL = "http://192.168.188.6:8891"


async def rerank(
        query: str,
        documents: list[str],
        grade_top_n: Optional[int] = None,
        return_documents: bool = True,
        grade_score_threshold: Optional[float] = None
) -> dict:
    """
    文档重排序服务，调用本地 embedding_rerank 服务（http://192.168.188.6:8891/v1/rerank）

    Args:
        query: 查询文本
        documents: 待排序的文档列表
        grade_top_n: 返回前N个文档，None则返回全部
        return_documents: 保留参数（服务端始终返回文档内容）
        grade_score_threshold: 相关性分数阈值（斩杀线），低于此分数的文档将被过滤，默认None不过滤

    Returns:
        {
            "output": {
                "results": [
                    {
                        "index": 0,
                        "relevance_score": 0.95,
                        "query": "查询文本",
                        "document": "文档内容"
                    },
                    ...
                ]
            }
        }

    Example:
        result = await rerank(
            query="什么是文本排序模型",
            documents=[
                "文本排序模型广泛用于搜索引擎和推荐系统中",
                "量子计算是计算科学的一个前沿领域"
            ],
            grade_top_n=1
        )
    """
    if not documents:
        logger.warning("文档列表为空，跳过重排序")
        return {"output": {"results": []}}

    endpoint = f"{EMBEDDING_RERANK_BASE_URL}/v1/rerank"
    payload = {
        "pairs": [{"query": query, "document": doc} for doc in documents]
    }
    headers = {"Content-Type": "application/json"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Rerank API 错误: {response.status}, {error_text}")
                    raise RuntimeError(f"Rerank API 请求失败: {response.status}")

                result = await response.json()

                # 响应格式: {"results": [{"index": 0, "relevance_score": 0.95, "query": "...", "document": "..."}, ...]}
                all_results = result.get("results", [])
                filtered_results = all_results

                # 1. 应用分数阈值过滤（斩杀线）
                if grade_score_threshold is not None:
                    original_count = len(filtered_results)
                    filtered_results = [
                        item for item in filtered_results
                        if item.get("relevance_score", 0) >= grade_score_threshold
                    ]
                    removed = original_count - len(filtered_results)
                    if removed:
                        logger.info(
                            f"应用斩杀线 {grade_score_threshold}：过滤掉 {removed} 个低分文档，"
                            f"保留 {len(filtered_results)} 个高质量文档"
                        )

                # 2. 按相关性分数降序排序
                filtered_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

                # 3. 应用top_n限制
                if grade_top_n is not None and len(filtered_results) > grade_top_n:
                    filtered_results = filtered_results[:grade_top_n]
                    logger.info(f"应用top_n={grade_top_n}：返回前 {grade_top_n} 个文档")

                logger.info(
                    f"重排序完成，处理了 {len(documents)} 个文档，"
                    f"返回 {len(filtered_results)} 个结果"
                )
                return {"output": {"results": filtered_results}}

    except asyncio.TimeoutError:
        logger.error("Rerank API 请求超时")
        raise RuntimeError("Rerank API 请求超时")
    except aiohttp.ClientError as e:
        logger.error(f"Rerank API 网络错误: {e}")
        raise RuntimeError(f"Rerank API 网络错误: {str(e)}")
    except Exception as e:
        logger.error(f"Rerank 处理失败: {e}")
        raise
