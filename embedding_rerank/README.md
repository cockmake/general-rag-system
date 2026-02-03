# Embedding & Rerank Service - 本地向量化服务

基于 vLLM 的高性能本地向量化和重排序服务，支持使用 GPU 加速的 Embedding 模型推理。

## 🆕 FastAPI服务模式（推荐）

现在支持通过 FastAPI 提供标准的 REST API 服务，兼容 OpenAI Embeddings API 格式。

### 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件修改配置

# 3. 启动服务
python start.py

# 或使用脚本启动
# Linux/Mac: bash run.sh
# Windows: run.bat
```

### API接口

#### 1. 健康检查
```bash
curl http://localhost:8890/health
```

#### 2. 生成Embedding（单个文本）
```bash
curl -X POST http://localhost:8890/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": "What is the capital of China?"
  }'
```

#### 3. 生成Embedding（批量）
```bash
curl -X POST http://localhost:8890/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": [
      "What is the capital of China?",
      "Explain gravity"
    ]
  }'
```

#### 4. 带指令的Embedding
```bash
curl -X POST http://localhost:8890/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": ["What is the capital of China?"],
    "instruction": "Given a web search query, retrieve relevant passages that answer the query"
  }'
```

### 响应格式

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [0.123, -0.456, ...]
    }
  ],
  "model": "Qwen/Qwen3-Embedding-0.6B",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

### 配置说明

通过环境变量配置（在 `.env` 文件中设置）：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `EMBEDDING_MODEL_NAME` | `Qwen/Qwen3-Embedding-0.6B` | 模型名称 |
| `EMBEDDING_GPU_MEMORY_UTILIZATION` | `0.4` | GPU显存占用比例（0-1） |
| `EMBEDDING_MAX_MODEL_LEN` | `3072` | 最大token长度 |
| `EMBEDDING_PORT` | `8890` | 服务端口 |
| `EMBEDDING_HOST` | `0.0.0.0` | 服务监听地址 |
| `EMBEDDING_DTYPE` | `float16` | 数据类型 |

### 测试服务

```bash
# 运行测试脚本
python test_service.py
```

### 集成到 rag-llm

在 `rag-llm` 项目的配置文件中添加：

```json
{
  "embedding": {
    "local": {
      "settings": {
        "base_url": "http://localhost:8890/v1",
        "api_key": "dummy",
        "provider": "openai",
        "dimensions": 1024
      },
      "text-embedding-0.6b": {}
    }
  }
}
```

然后在代码中使用：

```python
embedding_config = {
    'name': 'text-embedding-0.6b',
    'provider': 'local'
}
embeddings = get_embedding_instance(embedding_config)
```

---

## 简介

这是一个可选的本地向量化服务模块，适用于：
- 🔒 **高隐私要求** - 不希望文档内容发送到第三方 API
- 💰 **成本优化** - 大量文档向量化时避免 API 费用
- ⚡ **高性能需求** - 利用 GPU 加速批量处理
- 🎯 **定制化需求** - 使用特定领域的 Embedding 模型

## 技术栈

- **vLLM >= 0.8.5** - 高性能 LLM 推理引擎
- **PyTorch** - 深度学习框架
- **Qwen3-Embedding-4B** - 示例使用的 Embedding 模型（可替换）
- **CUDA** - GPU 加速（可选）

## 前置要求

### 硬件要求

- **GPU**：推荐 NVIDIA GPU（至少 8GB 显存）
  - Qwen3-Embedding-4B 需要约 6-8GB 显存
  - 更大的模型需要更多显存
- **内存**：至少 16GB RAM
- **存储**：模型文件约 10-15GB

### 软件要求

- Python 3.8+
- CUDA 11.8+ （如使用 GPU）
- cuDNN 相应版本

## 快速开始

### 1. 安装依赖

```bash
# 安装 vLLM（GPU 版本）
pip install vllm>=0.8.5

# 或安装 CPU 版本（性能较低）
pip install vllm>=0.8.5 --extra-index-url https://download.pytorch.org/whl/cpu

# 安装 PyTorch（如需要）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. 下载模型

```bash
# 使用 Hugging Face CLI
pip install huggingface_hub

# 下载 Qwen3-Embedding-4B 模型
huggingface-cli download Qwen/Qwen3-Embedding-4B

# 或在代码中自动下载（首次运行会下载）
```

### 3. 运行示例

```bash
python main.py
```

## 使用示例

### 基本向量化

```python
from vllm import LLM

# 初始化模型
model = LLM(model="Qwen/Qwen3-Embedding-4B", convert="embed")

# 准备文本
queries = [
    "What is the capital of China?",
    "Explain gravity"
]

documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts objects."
]

# 生成向量
outputs = model.embed(queries + documents)
embeddings = [o.outputs.embedding for o in outputs]

# 计算相似度
import torch
embeddings_tensor = torch.tensor(embeddings)
query_embeds = embeddings_tensor[:2]
doc_embeds = embeddings_tensor[2:]
scores = (query_embeds @ doc_embeds.T)
print(scores)
```

### 带指令的向量化

```python
def get_detailed_instruct(task_description: str, query: str) -> str:
    """为查询添加任务指令"""
    return f'Instruct: {task_description}\nQuery: {query}'

# 定义任务
task = 'Given a web search query, retrieve relevant passages that answer the query'

# 为查询添加指令
queries = [
    get_detailed_instruct(task, 'What is the capital of China?'),
    get_detailed_instruct(task, 'Explain gravity')
]

# 文档不需要指令
documents = [
    "The capital of China is Beijing.",
    "Gravity is a force that attracts objects."
]

# 生成向量并计算相似度
outputs = model.embed(queries + documents)
# ... 后续处理
```

## 集成到 RAG 系统

### 方式一：替换 rag-llm 中的 Embedding

在 `rag-llm/rag_utils.py` 中：

```python
from vllm import LLM

class LocalEmbedding:
    def __init__(self, model_name="Qwen/Qwen3-Embedding-4B"):
        self.model = LLM(model=model_name, convert="embed")
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        outputs = self.model.embed(texts)
        return [o.outputs.embedding for o in outputs]
    
    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

# 使用本地 Embedding
embedding = LocalEmbedding()
```

### 方式二：部署为独立服务

创建 FastAPI 服务：

```python
from fastapi import FastAPI
from vllm import LLM
from pydantic import BaseModel

app = FastAPI()
model = LLM(model="Qwen/Qwen3-Embedding-4B", convert="embed")

class EmbedRequest(BaseModel):
    texts: list[str]

@app.post("/embed")
async def embed(request: EmbedRequest):
    outputs = model.embed(request.texts)
    embeddings = [o.outputs.embedding for o in outputs]
    return {"embeddings": embeddings}

# 启动：uvicorn embedding_service:app --host 0.0.0.0 --port 8889
```

## 支持的模型

### Embedding 模型

- **Qwen/Qwen3-Embedding-4B** - 推荐，性能和质量平衡
- **BAAI/bge-large-zh-v1.5** - 中文优化
- **intfloat/e5-large-v2** - 英文优化
- **jinaai/jina-embeddings-v3** - 多语言支持

### 更换模型

```python
# 只需修改模型名称
model = LLM(model="BAAI/bge-large-zh-v1.5", convert="embed")
```

## 性能优化

### GPU 加速配置

```python
model = LLM(
    model="Qwen/Qwen3-Embedding-4B",
    convert="embed",
    tensor_parallel_size=1,  # GPU 数量
    gpu_memory_utilization=0.9,  # GPU 内存利用率
    dtype="float16"  # 使用半精度
)
```

### 批处理优化

```python
# 大批量处理时分批
def batch_embed(texts, batch_size=32):
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        outputs = model.embed(batch)
        embeddings.extend([o.outputs.embedding for o in outputs])
    return embeddings
```

## Docker 部署

### Dockerfile

```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

WORKDIR /app

# 安装 Python
RUN apt-get update && apt-get install -y python3 python3-pip

# 安装依赖
RUN pip install vllm>=0.8.5 torch

# 复制代码
COPY main.py .

# 下载模型（可选，也可以挂载）
# RUN huggingface-cli download Qwen/Qwen3-Embedding-4B

EXPOSE 8889

CMD ["python3", "main.py"]
```

### 运行

```bash
# 构建
docker build -t embedding-service:1.0.0 .

# 运行（需要 nvidia-docker）
docker run --gpus all -d -p 8889:8889 embedding-service:1.0.0
```

## 性能对比

### Embedding 速度对比（参考值）

| 方法 | 100 文档 | 1000 文档 | 10000 文档 |
|------|---------|----------|-----------|
| OpenAI API | ~5s | ~50s | ~500s |
| 本地 GPU (vLLM) | ~2s | ~15s | ~150s |
| 本地 CPU | ~30s | ~300s | ~3000s |

*实际速度取决于硬件配置和模型大小*

### 成本对比

- **OpenAI API**: $0.0001/1K tokens（约 $10/1M tokens）
- **本地部署**: GPU 电费 + 硬件折旧（一次性成本）
- **临界点**: 约 1000万 tokens 后本地部署更划算

## 常见问题

**Q: 没有 GPU 可以运行吗？**
A: 可以，但速度会非常慢，不推荐用于生产环境。

**Q: 如何选择合适的 Embedding 模型？**
A: 根据语言（中文/英文）、领域（通用/专业）和硬件（显存大小）选择。

**Q: vLLM 版本要求为什么是 0.8.5+？**
A: 0.8.5 版本开始支持 Embedding 模式（`convert="embed"`）。

**Q: 可以同时运行多个模型吗？**
A: 可以，但需要足够的显存，建议使用模型服务化方案。

## 相关资源

- [vLLM 官方文档](https://docs.vllm.ai/)
- [Qwen3-Embedding 模型](https://huggingface.co/Qwen/Qwen3-Embedding-4B)
- [Hugging Face Hub](https://huggingface.co/models?pipeline_tag=feature-extraction)

## 返回主文档

查看完整系统文档：[../README.md](../README.md)
