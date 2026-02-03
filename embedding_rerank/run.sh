#!/bin/bash
# Embedding Service 启动脚本

# 设置环境变量（可选，也可以使用.env文件）
# export EMBEDDING_MODEL_NAME="Qwen/Qwen3-Embedding-0.6B"
# export EMBEDDING_GPU_MEMORY_UTILIZATION=0.4
# export EMBEDDING_MAX_MODEL_LEN=3072
# export EMBEDDING_PORT=8890

# 激活虚拟环境（如果使用）
# source venv/bin/activate

# 启动服务
python start.py
