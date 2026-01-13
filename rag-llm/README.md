# RAG LLM Service - LLM服务

基于 FastAPI + LangChain 的大语言模型服务，提供文档解析、向量化和RAG问答功能。

## 技术栈

- Python 3.8+
- FastAPI（Web框架）
- LangChain（LLM应用框架）
- LangGraph（工作流编排）
- Milvus（向量检索）
- MinIO（文件存储）
- RabbitMQ（消息队列）
- PyMuPDF（PDF解析）
- Tesseract（OCR）

## 功能特性

- 📄 多格式文档解析（PDF、TXT等）
- 🔤 文本向量化（Embedding）
- 🔍 向量相似度检索
- 🤖 基于 RAG 的问答生成
- 📨 异步任务处理（通过 RabbitMQ）

## 快速开始

### 环境要求

```bash
python >= 3.8
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置文件

编辑 `model_config.json`：

```json
{
  "llm_model": "your-model-name",
  "embedding_model": "your-embedding-model",
  "milvus_host": "localhost",
  "milvus_port": 19530,
  "minio_endpoint": "localhost:9000",
  "minio_access_key": "your-access-key",
  "minio_secret_key": "your-secret-key",
  "rabbitmq_host": "localhost",
  "rabbitmq_port": 5672
}
```

### 运行服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

## API 接口

### 文档处理

- `POST /api/document/parse` - 解析文档
- `POST /api/document/embed` - 文本向量化

### RAG 问答

- `POST /api/rag/query` - RAG问答
- `POST /api/rag/search` - 向量检索

### 健康检查

- `GET /health` - 服务健康状态

## 项目结构

```
rag-llm/
├── main.py                      # 主程序入口
├── requirements.txt             # 依赖列表
├── model_config.json           # 模型配置
├── rag_utils.py                # RAG工具函数
├── milvus_utils.py             # Milvus操作
├── minio_utils.py              # MinIO操作
├── aiohttp_utils.py            # 异步HTTP工具
├── services/                    # 业务服务
│   └── ...
└── mq/                         # 消息队列相关
    └── ...
```

## 环境变量

可通过环境变量覆盖配置：

```bash
export MILVUS_HOST=localhost
export MILVUS_PORT=19530
export MINIO_ENDPOINT=localhost:9000
export RABBITMQ_HOST=localhost
```

## Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 启动服务
CMD ["python", "main.py"]
```

构建和运行：

```bash
docker build -t rag-llm:1.0.0 .
docker run -d -p 8000:8000 rag-llm:1.0.0
```

## 开发说明

### 添加新的文档解析器

在 `rag_utils.py` 中扩展解析逻辑。

### 自定义 Embedding 模型

修改 `model_config.json` 中的模型配置。

### 调试

设置日志级别：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 依赖服务

- Milvus: 向量数据库
- MinIO: 文件存储
- RabbitMQ: 消息队列（可选）

## 性能优化

- 使用异步处理提高并发
- 配置合理的批处理大小
- 启用向量索引优化检索速度
- 使用缓存减少重复计算
