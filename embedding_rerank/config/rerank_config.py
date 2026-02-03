"""
配置文件 - Rerank Service
直接修改此类中的属性进行配置
"""
from typing import Optional

from pydantic import BaseModel


class RerankConfig(BaseModel):
    """Rerank服务配置"""
    
    # 模型配置
    model_name: str = "Qwen/Qwen3-Reranker-0.6B"
    model_path: Optional[str] = None  # 可选：本地模型路径

    # GPU配置
    gpu_memory_utilization: float = 0.4
    max_model_len: int = 10000
    tensor_parallel_size: int = 1
    dtype: str = "float16"
    enable_prefix_caching: bool = True

    # Rerank特定配置
    max_length: int = 8192
    temperature: float = 0.0
    max_tokens: int = 1
    logprobs: int = 20

    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8891
    workers: int = 1

    # 批处理配置
    max_batch_size: int = 32
    batch_timeout_ms: int = 10

    # 日志配置
    log_level: str = "INFO"


# 创建全局配置实例
config = RerankConfig()
