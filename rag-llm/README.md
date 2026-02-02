# RAG LLM Service - AI 服务

基于 FastAPI + LangChain + LangGraph 的大语言模型服务，提供文档解析、向量化、RAG问答和流式响应等功能。

## 技术栈

- **Python 3.8+** - 编程语言
- **FastAPI** - 现代化异步 Web 框架
- **LangChain** - LLM 应用开发框架
- **LangGraph** - 工作流编排引擎
- **Milvus** - 向量数据库客户端
- **MinIO** - 对象存储客户端
- **RabbitMQ (pika)** - 消息队列
- **PyMuPDF (fitz)** - PDF 文档解析
- **pdfplumber** - PDF 表格提取
- **aiohttp** - 异步 HTTP 客户端
- **Uvicorn** - ASGI 服务器

## 功能特性

- 📄 **多格式文档解析** - 支持 PDF、TXT、Markdown 等格式
- 🔤 **文本向量化** - 集成多种 Embedding 模型（OpenAI、本地模型等）
- 🔍 **向量相似度检索** - 基于 Milvus 的高效检索
- 🤖 **RAG 问答生成** - 结合检索和生成的智能问答
- 📨 **异步任务处理** - 通过 RabbitMQ 处理文档向量化任务
- 🌊 **流式响应** - Server-Sent Events (SSE) 实时输出
- 🔗 **多 LLM 支持** - OpenAI、DeepSeek、通义千问、Gemini 等
- 📊 **文档重排序** - 提升检索质量

## 快速开始

### 环境要求

- Python >= 3.8
- pip 或 poetry
- GPU（可选，用于本地模型加速）

### 安装依赖

```bash
# 使用 pip
pip install -r requirements.txt

# 或使用 poetry（推荐）
poetry install
```

### 环境变量配置

⚠️ **重要**：`main.py` 中硬编码了基础设施连接信息，生产环境需修改或使用环境变量。

#### 方式一：修改 main.py（不推荐）

```python
# main.py 中的配置
os.environ["RABBITMQ_HOST"] = "192.168.188.6"
os.environ["RABBITMQ_PORT"] = "5678"
os.environ["RABBITMQ_USERNAME"] = "make"
os.environ["RABBITMQ_PASSWORD"] = "make20260101"

os.environ["MINIO_ENDPOINT"] = "192.168.188.6:9002"
os.environ["MINIO_ACCESS_KEY"] = "make"
os.environ["MINIO_SECRET_KEY"] = "make20260101"

os.environ["MILVUS_URI"] = "http://192.168.188.6:19530"
os.environ["MILVUS_TOKEN"] = "make:make5211314"
```

#### 方式二：使用环境变量（推荐）

```bash
# 设置环境变量
export RABBITMQ_HOST=localhost
export RABBITMQ_PORT=5672
export RABBITMQ_USERNAME=admin
export RABBITMQ_PASSWORD=your_password

export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=your_access_key
export MINIO_SECRET_KEY=your_secret_key

export MILVUS_URI=http://localhost:19530
export MILVUS_TOKEN=username:password

# 或创建 .env 文件（需安装 python-dotenv）
```

### 模型配置

#### 1. 复制配置模板

```bash
cp model_config.json.example model_config.json
```

#### 2. 编辑 model_config.json

```json
{
  "models": {
    "openai": {
      "api_key": "sk-your-openai-api-key",
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-4"
    },
    "deepseek": {
      "api_key": "sk-your-deepseek-api-key",
      "base_url": "https://api.deepseek.com",
      "model": "deepseek-chat"
    },
    "qwen": {
      "api_key": "sk-your-qwen-api-key",
      "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
      "model": "qwen-max"
    },
    "gemini": {
      "api_key": "your-gemini-api-key",
      "model": "gemini-pro"
    }
  },
  "embedding": {
    "provider": "openai",
    "model": "text-embedding-ada-002"
  }
}
```

⚠️ **不要将 model_config.json 提交到 Git！**

### 运行服务

#### 方式一：使用 Uvicorn（推荐生产环境）

```bash
# 单进程
uvicorn main:app --host 0.0.0.0 --port 8888

# 多进程（提高并发）
uvicorn main:app --host 0.0.0.0 --port 8888 --workers 2

# 开发模式（自动重载）
uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

#### 方式二：直接运行 Python

```bash
python main.py
```

服务将在 `http://localhost:8888` 启动（注意：端口是 8888，不是 8000）。

### 验证服务

```bash
# 健康检查
curl http://localhost:8888/health

# 查看服务信息
curl http://localhost:8888/rag/
```

## API 接口

### 聊天服务（Chat）

#### 流式对话
- `POST /rag/chat/stream` - 流式 RAG 问答
  - 参数：`question`, `kb_id`, `conversation_id`
  - 返回：Server-Sent Events (SSE) 流

#### 非流式对话
- `POST /rag/chat` - 普通 RAG 问答
  - 参数：`question`, `kb_id`
  - 返回：JSON 格式回答

### 文档处理（通过 RabbitMQ）

- 文档上传后自动触发向量化任务
- 异步处理，支持大文件
- 任务队列：`document_vectorization_queue`

### 健康检查

- `GET /health` - 服务健康状态
- 返回：`{"status": "healthy"}`

### 调用示例

#### 流式对话

```bash
curl -X POST http://localhost:8888/rag/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是RAG？",
    "kb_id": 1,
    "conversation_id": 123
  }'
```

#### 使用 Python 客户端

```python
import requests
import json

url = "http://localhost:8888/rag/chat/stream"
data = {
    "question": "什么是RAG？",
    "kb_id": 1,
    "conversation_id": 123
}

response = requests.post(url, json=data, stream=True)
for line in response.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        if decoded_line.startswith('data: '):
            json_data = json.loads(decoded_line[6:])
            print(json_data.get('content', ''), end='', flush=True)
```

## 项目结构

```
rag-llm/
├── main.py                          # FastAPI 应用入口
├── requirements.txt                 # Python 依赖
├── model_config.json                # 模型配置（需创建，已在 .gitignore）
├── model_config.json.example        # 配置模板
├── run.log                          # 运行日志
│
├── services/                        # 业务服务
│   ├── chat/                        # 聊天服务模块
│   │   └── chat_service.py          # 聊天路由和逻辑
│   └── __pycache__/
│
├── mq/                              # 消息队列
│   ├── consumer.py                  # RabbitMQ 消费者
│   └── producer.py                  # RabbitMQ 生产者
│
├── rag_utils.py                     # RAG 工具函数
│   ├── 文档解析（PDF、TXT）
│   ├── 文本分块（Chunking）
│   ├── 向量化（Embedding）
│   └── 检索增强生成
│
├── milvus_utils.py                  # Milvus 向量数据库操作
│   ├── 集合管理
│   ├── 向量插入
│   └── 相似度搜索
│
├── minio_utils.py                   # MinIO 对象存储操作
│   ├── 文件上传
│   ├── 文件下载
│   └── 桶管理
│
├── openai_utils.py                  # OpenAI API 封装
├── gemini_utils.py                  # Gemini API 封装
├── aiohttp_utils.py                 # 异步 HTTP 工具
├── utils.py                         # 通用工具函数
├── wrapper.py                       # 装饰器和包装器
├── dependencies.py                  # FastAPI 依赖注入
│
├── t.py                             # 测试脚本
└── __pycache__/                     # Python 缓存
```

## 核心功能说明

### 文档向量化流程

1. **文档上传** - 用户通过 rag-server 上传文档到 MinIO
2. **任务入队** - rag-server 发送向量化任务到 RabbitMQ
3. **文档下载** - rag-llm 从 MinIO 下载文档
4. **文档解析** - 使用 PyMuPDF/pdfplumber 解析 PDF
5. **文本分块** - 按语义切分文本（支持多种策略）
6. **向量化** - 调用 Embedding 模型生成向量
7. **存储** - 向量和元数据存入 Milvus
8. **状态更新** - 通知 rag-server 任务完成

### RAG 问答流程

1. **问题向量化** - 将用户问题转换为向量
2. **相似度检索** - 从 Milvus 检索相关文档片段（Top-K）
3. **重排序**（可选）- 使用 Rerank 模型优化结果
4. **上下文构建** - 组装检索结果和对话历史
5. **LLM 生成** - 调用大模型生成回答
6. **流式返回** - 通过 SSE 实时返回生成内容

## Docker 部署

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 8888

# 启动服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888", "--workers", "2"]
```

### 构建和运行

```bash
# 构建镜像
docker build -t rag-llm:1.0.0 .

# 运行容器
docker run -d -p 8888:8888 \
  -e RABBITMQ_HOST=rabbitmq \
  -e MINIO_ENDPOINT=minio:9000 \
  -e MILVUS_URI=http://milvus:19530 \
  -v ./model_config.json:/app/model_config.json:ro \
  -v ./logs:/app/logs \
  --name rag-llm \
  rag-llm:1.0.0
```

### Docker Compose

```yaml
version: '3.8'

services:
  rag-llm:
    build: .
    ports:
      - "8888:8888"
    environment:
      - RABBITMQ_HOST=rabbitmq
      - RABBITMQ_PORT=5672
      - MINIO_ENDPOINT=minio:9000
      - MILVUS_URI=http://milvus:19530
    volumes:
      - ./model_config.json:/app/model_config.json:ro
      - ./logs:/app/logs
    depends_on:
      - rabbitmq
      - minio
      - milvus
    restart: unless-stopped
```

## 开发指南

### 添加新的文档解析器

在 `rag_utils.py` 中扩展 `parse_document` 函数：

```python
def parse_document(file_path: str, file_type: str) -> str:
    if file_type == 'pdf':
        return parse_pdf(file_path)
    elif file_type == 'txt':
        return parse_txt(file_path)
    elif file_type == 'docx':  # 新增
        return parse_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
```

### 自定义 Embedding 模型

修改 `model_config.json` 或在代码中指定：

```python
from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-zh-v1.5",
    model_kwargs={'device': 'cuda'}
)
```

### 添加新的 LLM Provider

1. 在 `model_config.json` 中添加配置
2. 创建对应的 `xxx_utils.py` 文件
3. 在 RAG 流程中集成

### 调试技巧

#### 启用详细日志

```python
# 在 main.py 中修改日志级别
logging.basicConfig(
    level=logging.DEBUG,  # 改为 DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='run.log',
    encoding='utf-8'
)
```

#### 测试单个模块

```bash
# 测试 Milvus 连接
python -c "from milvus_utils import test_connection; test_connection()"

# 测试 MinIO 连接
python -c "from minio_utils import test_connection; test_connection()"
```

### 性能优化

1. **批量向量化** - 使用批处理减少 API 调用
2. **异步处理** - 充分利用 asyncio 和 aiohttp
3. **连接池** - 复用 HTTP 连接和数据库连接
4. **缓存策略** - 缓存常见查询的向量结果
5. **模型选择** - 根据场景选择合适的模型（速度 vs 质量）

### 常见问题

**Q: RabbitMQ 连接失败？**
A: 检查 RabbitMQ 是否启动，用户名密码是否正确，防火墙是否开放端口。

**Q: Milvus 插入向量失败？**
A: 确认集合是否已创建，向量维度是否匹配，是否有足够权限。

**Q: 文档解析乱码？**
A: 检查文档编码，PDF 可能需要 OCR，中文字符需要正确的字体支持。

**Q: 流式响应中断？**
A: 检查网络稳定性，增加超时时间，确保前端正确处理 SSE 连接。

**Q: 为什么端口是 8888 而不是 8000？**
A: 在 `main.py` 顶部注释中明确说明了使用 8888 端口，这是为了与 rag-server 配置保持一致。

## 相关资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [LangChain 文档](https://python.langchain.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [Milvus 文档](https://milvus.io/docs)
- [MinIO 文档](https://min.io/docs/minio/linux/index.html)

## 返回主文档

查看完整系统文档：[../README.md](../README.md)
