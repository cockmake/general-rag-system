import asyncio
import logging
from typing import Optional, Dict

from langchain_core.embeddings import Embeddings
from langchain_milvus import Milvus

logger = logging.getLogger(__name__)


class MilvusClientManager:
    """Milvus连接管理器，实现多知识库连接的复用"""

    _instances: Dict[str, Milvus] = {}
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(
            cls,
            user_id: int,
            kb_id: int,
            milvus_uri: str,
            milvus_token: str,
            embeddings: Embeddings
    ) -> Optional[Milvus]:
        """
        获取复用的Milvus实例
        
        Args:
            user_id: 用户ID
            kb_id: 知识库ID
            milvus_uri: Milvus URI
            milvus_token: Milvus Token
            embeddings: 嵌入模型实例
            
        Returns:
            Milvus实例或None
        """
        db_name = f"group_{user_id // 1000}"
        collection_name = f"kb_{kb_id}"
        key = f"{db_name}_{collection_name}"

        # 检查缓存
        if key in cls._instances:
            return cls._instances[key]

        async with cls._lock:
            # 双重检查
            if key in cls._instances:
                return cls._instances[key]

            try:
                # 建立新连接
                vector_store = Milvus(
                    embedding_function=embeddings,
                    connection_args={
                        "uri": milvus_uri,
                        "token": milvus_token,
                        "db_name": db_name,
                    },
                    collection_name=collection_name,
                    auto_id=True,
                )

                cls._instances[key] = vector_store
                logger.info(f"创建新的Milvus实例: {key}")
                return vector_store
            except Exception as e:
                logger.error(f"连接 Milvus 失败 ({key}): {e}")
                return None

    @classmethod
    async def close_all(cls):
        """关闭所有连接"""
        async with cls._lock:
            for key, store in cls._instances.items():
                try:
                    if hasattr(store, 'aclient'):
                        await store.aclient.close()
                except Exception as e:
                    logger.error(f"关闭 Milvus 连接失败 ({key}): {e}")
            cls._instances.clear()
