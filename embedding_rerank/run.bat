@echo off
REM Embedding Service 启动脚本 (Windows)

echo ============================================================
echo Embedding Service Starting...
echo ============================================================

REM 设置环境变量（可选，也可以使用.env文件）
REM set EMBEDDING_MODEL_NAME=Qwen/Qwen3-Embedding-0.6B
REM set EMBEDDING_GPU_MEMORY_UTILIZATION=0.4
REM set EMBEDDING_MAX_MODEL_LEN=3072
REM set EMBEDDING_PORT=8890

REM 激活虚拟环境（如果使用）
REM call venv\Scripts\activate.bat

REM 启动服务
python start.py

pause
