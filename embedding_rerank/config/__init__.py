"""
配置模块
"""
from config.embedding_config import config as embedding_config
from config.rerank_config import config as rerank_config

__all__ = ['embedding_config', 'rerank_config']
