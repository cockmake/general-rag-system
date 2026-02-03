"""
配置文件 - Embedding Service
支持通过环境变量或配置文件进行配置
"""
from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class EmbeddingConfig(BaseSettings):
    """Embedding服务配置"""
    
    model_config = ConfigDict(
        env_prefix="EMBEDDING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # 忽略额外的环境变量
    )

    # 模型配置
    model_name: str = "Qwen/Qwen3-Embedding-0.6B"
    model_path: Optional[str] = None  # 可选：本地模型路径

    # GPU配置
    gpu_memory_utilization: float = 0.4
    max_model_len: int = 3072
    tensor_parallel_size: int = 1
    dtype: str = "float16"

    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8890
    workers: int = 1

    # 批处理配置
    max_batch_size: int = 32
    batch_timeout_ms: int = 10

    # 日志配置
    log_level: str = "INFO"


# 创建全局配置实例
config = EmbeddingConfig()
