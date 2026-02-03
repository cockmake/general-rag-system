# Embedding Service API 文档

## 概述

Embedding Service 是一个基于 vLLM 的高性能向量化服务，提供与 OpenAI Embeddings API 兼容的接口。

- **版本**: 1.0.0
- **默认端口**: 8890
- **默认模型**: Qwen/Qwen3-Embedding-0.6B
- **向量维度**: 1024 维

## 端点列表

### 1. GET / - 根路径

获取服务基本信息。

**请求**
```bash
curl http://localhost:8890/
```

**响应**
```json
{
  "service": "Embedding Service",
  "version": "1.0.0",
  "model": "Qwen/Qwen3-Embedding-0.6B",
  "status": "running"
}
```

---

### 2. GET /health - 健康检查

检查服务健康状态和配置信息。

**请求**
```bash
curl http://localhost:8890/health
```

**响应**
```json
{
  "status": "healthy",
  "model": "Qwen/Qwen3-Embedding-0.6B",
  "gpu_memory_utilization": 0.4,
  "max_model_len": 3072,
  "device": "cuda"
}
```

**状态码**
- `200 OK` - 服务正常
- `503 Service Unavailable` - 模型未加载

---

### 3. POST /v1/embeddings - 生成向量（标准接口）

生成文本的向量表示（兼容 OpenAI API 格式）。

**请求**

```bash
curl -X POST http://localhost:8890/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": "你的文本内容",
    "instruction": "可选的任务指令"
  }'
```

**请求体参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `input` | `string \| string[]` | ✅ | 单个文本或文本列表 |
| `instruction` | `string` | ❌ | 任务指令，添加到查询文本前 |
| `model` | `string` | ❌ | 模型名称（当前版本忽略） |

**请求示例**

*单个文本*
```json
{
  "input": "What is the capital of China?"
}
```

*批量文本*
```json
{
  "input": [
    "What is the capital of China?",
    "Explain gravity",
    "What is machine learning?"
  ]
}
```

*带指令的文本*
```json
{
  "input": ["What is the capital of China?"],
  "instruction": "Given a web search query, retrieve relevant passages that answer the query"
}
```

**响应**

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [0.123, -0.456, 0.789, ...]
    }
  ],
  "model": "Qwen/Qwen3-Embedding-0.6B",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| `object` | `string` | 固定值 "list" |
| `data` | `array` | 向量数据列表 |
| `data[].object` | `string` | 固定值 "embedding" |
| `data[].index` | `integer` | 在输入列表中的索引位置 |
| `data[].embedding` | `float[]` | 向量数据（1024维） |
| `model` | `string` | 使用的模型名称 |
| `usage.prompt_tokens` | `integer` | 输入token数 |
| `usage.total_tokens` | `integer` | 总token数 |

**状态码**
- `200 OK` - 成功
- `400 Bad Request` - 请求参数错误
- `500 Internal Server Error` - 服务器内部错误
- `503 Service Unavailable` - 模型未加载

---

### 4. POST /embeddings - 生成向量（简化接口）

与 `/v1/embeddings` 功能完全相同，提供更简洁的路径。

**请求**
```bash
curl -X POST http://localhost:8890/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "你的文本"}'
```

---

## 使用示例

### Python (requests)

```python
import requests

# 单个文本
response = requests.post(
    "http://localhost:8890/v1/embeddings",
    json={"input": "What is AI?"}
)
result = response.json()
embedding = result["data"][0]["embedding"]
print(f"向量维度: {len(embedding)}")

# 批量文本
response = requests.post(
    "http://localhost:8890/v1/embeddings",
    json={
        "input": [
            "What is AI?",
            "What is machine learning?"
        ]
    }
)
result = response.json()
for item in result["data"]:
    print(f"Index {item['index']}: {len(item['embedding'])} dimensions")
```

### Python (httpx - 异步)

```python
import httpx
import asyncio

async def get_embeddings(texts):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8890/v1/embeddings",
            json={"input": texts},
            timeout=30.0
        )
        return response.json()

# 使用
result = asyncio.run(get_embeddings([
    "What is AI?",
    "What is machine learning?"
]))
```

### JavaScript (fetch)

```javascript
async function getEmbeddings(texts) {
  const response = await fetch('http://localhost:8890/v1/embeddings', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      input: texts
    })
  });
  
  return await response.json();
}

// 使用
const result = await getEmbeddings([
  'What is AI?',
  'What is machine learning?'
]);
console.log(result);
```

### cURL

```bash
# 单个文本
curl -X POST http://localhost:8890/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "What is AI?"}'

# 批量文本
curl -X POST http://localhost:8890/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": [
      "What is AI?",
      "What is machine learning?"
    ]
  }'

# 带指令
curl -X POST http://localhost:8890/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": ["search query"],
    "instruction": "Given a web search query, retrieve relevant passages"
  }'
```

---

## 错误处理

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

### 常见错误

**400 Bad Request**
```json
{
  "detail": "Input cannot be empty"
}
```

**503 Service Unavailable**
```json
{
  "detail": "Model not loaded"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Internal error: [具体错误信息]"
}
```

---

## 性能优化建议

### 1. 批量处理
尽量使用批量请求而非多次单个请求：

❌ **不推荐**
```python
# 多次请求
for text in texts:
    response = requests.post(url, json={"input": text})
```

✅ **推荐**
```python
# 批量请求
response = requests.post(url, json={"input": texts})
```

### 2. 并发控制
如果必须并发请求，建议限制并发数：

```python
import asyncio
from asyncio import Semaphore

async def get_embedding_with_limit(text, semaphore):
    async with semaphore:
        # 发送请求
        pass

# 限制并发为5
semaphore = Semaphore(5)
tasks = [get_embedding_with_limit(text, semaphore) for text in texts]
results = await asyncio.gather(*tasks)
```

### 3. 连接复用
使用连接池复用TCP连接：

```python
import requests

session = requests.Session()
# 复用session发送多个请求
for batch in batches:
    response = session.post(url, json={"input": batch})
```

---

## 集成指南

### 与 LangChain 集成

```python
from langchain_community.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-0.6b",
    openai_api_base="http://localhost:8890/v1",
    openai_api_key="dummy"  # 本地服务不需要真实key
)

# 使用
vector = embeddings.embed_query("你的查询文本")
vectors = embeddings.embed_documents(["文档1", "文档2"])
```

### 与 rag-llm 集成

在 `model_config.json` 中添加：

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

---

## 配置参考

### 环境变量完整列表

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `EMBEDDING_MODEL_NAME` | `Qwen/Qwen3-Embedding-0.6B` | 模型名称或路径 |
| `EMBEDDING_MODEL_PATH` | `None` | 本地模型路径（可选） |
| `EMBEDDING_GPU_MEMORY_UTILIZATION` | `0.4` | GPU显存占用比例 |
| `EMBEDDING_MAX_MODEL_LEN` | `3072` | 最大序列长度 |
| `EMBEDDING_TENSOR_PARALLEL_SIZE` | `1` | GPU并行数 |
| `EMBEDDING_DTYPE` | `float16` | 数据类型 |
| `EMBEDDING_HOST` | `0.0.0.0` | 监听地址 |
| `EMBEDDING_PORT` | `8890` | 服务端口 |
| `EMBEDDING_WORKERS` | `1` | Worker数量 |
| `EMBEDDING_MAX_BATCH_SIZE` | `32` | 最大批量大小 |
| `EMBEDDING_BATCH_TIMEOUT_MS` | `10` | 批处理超时 |
| `EMBEDDING_LOG_LEVEL` | `INFO` | 日志级别 |

---

## 限制和注意事项

1. **最大输入长度**: 3072 tokens（可配置）
2. **向量维度**: 1024（由模型决定）
3. **并发处理**: 建议限制并发请求数，避免显存溢出
4. **显存占用**: 默认占用40%显存（可配置）
5. **批量大小**: 建议单次不超过32个文本

---

## 常见问题

**Q: 如何查看服务日志？**  
A: 日志直接输出到控制台，可以使用重定向保存：
```bash
python start.py > logs/service.log 2>&1
```

**Q: 如何更换模型？**  
A: 修改环境变量 `EMBEDDING_MODEL_NAME` 或配置文件中的 `model_name`

**Q: 支持多GPU吗？**  
A: 支持，设置 `EMBEDDING_TENSOR_PARALLEL_SIZE` 为GPU数量

**Q: 如何优化性能？**  
A: 
1. 增加 `GPU_MEMORY_UTILIZATION`
2. 使用批量请求
3. 启用 flash-attention（需要编译）
4. 使用 `dtype="bfloat16"` 或 `"float16"`

---

## API 版本历史

- **v1.0.0** (2024-02) - 初始版本
  - 支持单个和批量文本embedding
  - 支持任务指令
  - 兼容 OpenAI API 格式
