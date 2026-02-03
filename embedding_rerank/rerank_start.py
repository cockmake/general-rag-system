"""
Rerank Service 启动脚本
"""
import os
import sys
import logging
import uvicorn
from config.rerank_config import config

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """启动服务"""
    logger.info("=" * 70)
    logger.info("Rerank Service Configuration:")
    logger.info("=" * 70)
    logger.info(f"Model: {config.model_name}")
    logger.info(f"GPU Memory Utilization: {config.gpu_memory_utilization}")
    logger.info(f"Max Model Length: {config.max_model_len}")
    logger.info(f"Tensor Parallel Size: {config.tensor_parallel_size}")
    logger.info(f"DType: {config.dtype}")
    logger.info(f"Enable Prefix Caching: {config.enable_prefix_caching}")
    logger.info(f"Max Length: {config.max_length}")
    logger.info(f"Host: {config.host}")
    logger.info(f"Port: {config.port}")
    logger.info(f"Workers: {config.workers}")
    logger.info(f"Max Batch Size: {config.max_batch_size}")
    logger.info(f"Log Level: {config.log_level}")
    logger.info("=" * 70)
    
    # 启动服务
    uvicorn.run(
        "service.rerank_service:app",
        host=config.host,
        port=config.port,
        workers=config.workers,
        log_level=config.log_level.lower(),
        access_log=True,
        reload=False  # 生产环境不启用热重载
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start service: {e}", exc_info=True)
        sys.exit(1)
