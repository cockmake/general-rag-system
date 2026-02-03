# Rerank Service API 文档

## 基本信息

- **Base URL**: `http://localhost:8891`
- **协议**: HTTP/HTTPS
- **内容类型**: `application/json`

## API端点

### 1. 根路径

获取服务基本信息。

**端点**: `GET /`

**响应示例**:
```json
{
  "service": "Rerank Service",
  "version": "1.0.0",
  "model": "Qwen/Qwen3-Reranker-0.6B",
  "status": "running"
}
```

---

### 2. 健康检查

检查服务健康状态和配置信息。

**端点**: `GET /health`

**响应示例**:
```json
{
  "status": "healthy",
  "model": "Qwen/Qwen3-Reranker-0.6B",
  "gpu_memory_utilization": 0.4,
  "max_model_len": 10000,
  "device": "cuda"
}
```

**状态码**:
- `200`: 服务健康
- `503`: 模型未加载

---

### 3. 重排序 (标准端点)

对查询-文档对进行重排序，返回相关性分数。

**端点**: `POST /v1/rerank`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pairs | Array[QueryDocPair] | ✓ | 查询-文档对列表 |
| instruction | String | ✗ | 任务指令，默认为检索任务 |
| model | String | ✗ | 模型名称（当前忽略） |

**QueryDocPair 结构**:
```json
{
  "query": "查询文本",
  "document": "文档文本"
}
```

**完整请求示例**:
```json
{
  "pairs": [
    {
      "query": "What is the capital of China?",
      "document": "The capital of China is Beijing."
    },
    {
      "query": "What is the capital of China?",
      "document": "Shanghai is the largest city in China."
    },
    {
      "query": "What is the capital of China?",
      "document": "China has a long history."
    }
  ],
  "instruction": "Given a web search query, retrieve relevant passages that answer the query"
}
```

**响应示例**:
```json
{
  "results": [
    {
      "index": 0,
      "score": 0.9876,
      "query": "What is the capital of China?",
      "document": "The capital of China is Beijing."
    },
    {
      "index": 1,
      "score": 0.4321,
      "query": "What is the capital of China?",
      "document": "Shanghai is the largest city in China."
    },
    {
      "index": 2,
      "score": 0.1234,
      "query": "What is the capital of China?",
      "document": "China has a long history."
    }
  ],
  "model": "Qwen/Qwen3-Reranker-0.6B",
  "processing_time": 0.125
}
```

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| results | Array | 重排序结果列表 |
| results[].index | Integer | 原始输入中的索引位置 |
| results[].score | Float | 相关性分数 (0-1) |
| results[].query | String | 查询文本 |
| results[].document | String | 文档文本 |
| model | String | 使用的模型名称 |
| processing_time | Float | 处理时间（秒） |

**状态码**:
- `200`: 成功
- `400`: 请求参数错误
- `500`: 服务器内部错误
- `503`: 模型未加载

**错误响应示例**:
```json
{
  "detail": "Pairs cannot be empty"
}
```

---

### 4. 重排序 (简化端点)

功能与 `/v1/rerank` 完全相同，提供更简洁的路径。

**端点**: `POST /rerank`

**请求/响应**: 与 `/v1/rerank` 相同

---

## 使用示例

### cURL

```bash
# 单个查询-文档对
curl -X POST http://localhost:8891/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "pairs": [
      {
        "query": "Python编程",
        "document": "Python是一种高级编程语言"
      }
    ]
  }'

# 批量查询-文档对
curl -X POST http://localhost:8891/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "pairs": [
      {"query": "Python编程", "document": "Python是一种编程语言"},
      {"query": "Python编程", "document": "Java也是一种编程语言"},
      {"query": "Python编程", "document": "机器学习很流行"}
    ],
    "instruction": "检索与编程相关的文档"
  }'
```

### Python

```python
import requests

# 基础用法
def rerank_documents(query, documents):
    pairs = [{"query": query, "document": doc} for doc in documents]
    response = requests.post(
        "http://localhost:8891/v1/rerank",
        json={"pairs": pairs}
    )
    return response.json()

# 使用示例
query = "Python编程语言"
documents = [
    "Python是一种高级编程语言，广泛用于数据科学",
    "Java是另一种流行的编程语言",
    "机器学习是人工智能的一个分支"
]

results = rerank_documents(query, documents)

# 按分数排序
sorted_results = sorted(
    results["results"],
    key=lambda x: x["score"],
    reverse=True
)

for i, result in enumerate(sorted_results, 1):
    print(f"{i}. Score: {result['score']:.4f}")
    print(f"   Document: {result['document']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function rerankDocuments(query, documents) {
  const pairs = documents.map(doc => ({
    query: query,
    document: doc
  }));
  
  const response = await axios.post('http://localhost:8891/v1/rerank', {
    pairs: pairs
  });
  
  return response.data;
}

// 使用示例
const query = "Python编程语言";
const documents = [
  "Python是一种高级编程语言",
  "Java是另一种流行的编程语言",
  "机器学习是人工智能的一个分支"
];

rerankDocuments(query, documents)
  .then(results => {
    // 按分数排序
    const sorted = results.results.sort((a, b) => b.score - a.score);
    sorted.forEach((result, i) => {
      console.log(`${i+1}. Score: ${result.score.toFixed(4)}`);
      console.log(`   Document: ${result.document}`);
    });
  })
  .catch(error => console.error('Error:', error));
```

---

## 性能指标

### 延迟

| 批量大小 | 平均延迟 | 说明 |
|---------|---------|------|
| 1 | 100-200ms | 单次推理 |
| 10 | 300-500ms | 小批量 |
| 32 | 800-1200ms | 大批量 |

### 吞吐量

- **单GPU (A100)**: ~500-1000 pairs/s
- **单GPU (V100)**: ~300-600 pairs/s
- **CPU**: ~10-20 pairs/s

*实际性能取决于硬件配置和输入长度*

---

## 最佳实践

### 1. 批量处理

将多个查询-文档对打包成一个请求以提高吞吐量：

```python
# ✓ 推荐：批量请求
pairs = [{"query": q, "document": d} for q, d in zip(queries, documents)]
response = requests.post(url, json={"pairs": pairs})

# ✗ 不推荐：多次单独请求
for q, d in zip(queries, documents):
    response = requests.post(url, json={"pairs": [{"query": q, "document": d}]})
```

### 2. 相关性分数解释

- **0.8 - 1.0**: 高度相关
- **0.5 - 0.8**: 中度相关
- **0.0 - 0.5**: 低度相关

### 3. 输入长度限制

- 最大输入长度: 8192 tokens (可通过配置调整)
- 过长的输入会被截断
- 建议预处理文本保持合理长度

### 4. 错误处理

```python
try:
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    results = response.json()
except requests.exceptions.Timeout:
    print("请求超时")
except requests.exceptions.HTTPError as e:
    print(f"HTTP错误: {e.response.status_code}")
    print(f"错误详情: {e.response.json()}")
except Exception as e:
    print(f"未知错误: {e}")
```

---

## 常见问题

### Q: 分数的含义是什么？

分数表示文档与查询的相关性概率，范围0-1。分数越高表示越相关。

### Q: 如何处理空查询或文档？

API会返回400错误。请确保所有查询和文档都非空。

### Q: 是否支持中文？

是的，模型支持多语言，包括中文。

### Q: 批量大小有限制吗？

建议批量大小不超过32，过大的批量可能导致内存问题。

### Q: 如何提高性能？

1. 使用批量请求
2. 启用GPU
3. 增加GPU内存利用率
4. 使用多GPU（设置tensor_parallel_size）

---

## 更新日志

### v1.0.0 (2026-02-03)
- 初始版本发布
- 支持基本的重排序功能
- 支持批量处理
- 兼容OpenAI风格的API

---

## 技术支持

如有问题或建议，请参考：
- [README文档](RerankREADME.md)
- [快速启动指南](RerankQUICKSTART.md)
