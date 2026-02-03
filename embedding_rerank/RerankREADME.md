# Rerank Service - 完整文档

基于vLLM和Qwen3-Reranker-0.6B的高性能重排序服务

## 目录

- [概述](#概述)
- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [API接口](#api接口)
- [性能优化](#性能优化)
- [故障排除](#故障排除)
- [最佳实践](#最佳实践)
- [更新日志](#更新日志)

## 概述

Rerank Service是一个生产级的文档重排序服务，提供：

### 核心特性

- 🚀 **高性能推理**: 基于vLLM引擎，支持GPU加速
- 📊 **精准排序**: 基于Qwen3-Reranker-0.6B模型
- 📦 **批量处理**: 高效的批量重排序
- 🔧 **灵活配置**: 支持环境变量和配置文件
- 🌐 **标准API**: RESTful API设计
- 📈 **完整监控**: 详细的日志和性能指标
- 🔄 **生产就绪**: 健康检查、优雅关闭等

### 技术栈

- **推理引擎**: vLLM 0.8.5+
- **模型**: Qwen3-Reranker-0.6B
- **框架**: FastAPI + Uvicorn
- **配置**: Pydantic
- **语言**: Python 3.8+

### 应用场景

1. **搜索引擎**: 对初排结果进行精排序
2. **推荐系统**: 提高推荐质量
3. **问答系统**: 找到最相关的答案
4. **文档检索**: 精确匹配文档相关性

## 系统要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 4核 | 8核+ |
| 内存 | 8GB | 16GB+ |
| GPU | - | NVIDIA GPU (4GB+ 显存) |
| 磁盘 | 10GB | 20GB+ SSD |

### 软件要求

- **操作系统**: Linux (推荐), macOS, Windows
- **Python**: 3.8, 3.9, 3.10, 3.11
- **CUDA**: 11.8+ (使用GPU时)
- **驱动**: NVIDIA Driver 450.80.02+

### 依赖包

```txt
vllm>=0.8.5
fastapi>=0.100.0
uvicorn>=0.23.0
transformers>=4.30.0
torch>=2.0.0
pydantic>=2.0.0
```

## 快速开始

### 1. 安装

```bash
# 安装依赖
pip install vllm>=0.8.5 fastapi uvicorn transformers torch pydantic

# 克隆代码（如果需要）
git clone <repository-url>
cd embedding_rerank
```

### 2. 配置

直接编辑配置文件 `config/rerank_config.py` 进行配置：

```bash
nano config/rerank_config.py
```

### 3. 启动

```bash
python rerank_start.py
```

启动成功后，服务将在 `http://0.0.0.0:8891` 运行。

### 4. 验证

```bash
# 健康检查
curl http://localhost:8891/health

# 重排序测试
curl -X POST http://localhost:8891/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "pairs": [
      {
        "query": "What is Python?",
        "document": "Python is a programming language."
      }
    ]
  }'
```

## 配置说明

### 配置方式

请直接修改 `config/rerank_config.py` 文件中的 `RerankConfig` 类属性。

### 完整配置选项

#### 模型配置

```python
# 模型名称（HuggingFace模型ID）
model_name: str = "Qwen/Qwen3-Reranker-0.6B"

# 本地模型路径（可选，优先于model）
model_path: Optional[str] = None
```

#### GPU配置

```python
# GPU内存使用率 (0.0-1.0)
gpu_memory_utilization: float = 0.4

# 最大模型长度（tokens）
max_model_len: int = 10000

# 张量并行大小（GPU数量）
tensor_parallel_size: int = 1

# 数据类型
dtype: str = "float16"  # 可选: float16, bfloat16, float32

# 启用前缀缓存
enable_prefix_caching: bool = True
```

#### Rerank特定配置

```python
# 最大输入长度（tokens）
max_length: int = 8192

# 采样温度
temperature: float = 0.0

# 最大生成token数
max_tokens: int = 1

# Logprobs数量
logprobs: int = 20
```

#### 服务配置

```python
# 监听地址
host: str = "0.0.0.0"

# 服务端口
port: int = 8891

# 工作进程数（推荐设为1）
workers: int = 1
```

#### 批处理配置

```python
# 最大批处理大小
max_batch_size: int = 32

# 批处理超时（毫秒）
batch_timeout_ms: int = 10
```

#### 日志配置

```python
# 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
log_level: str = "INFO"
```

### 配置示例

**生产环境**
修改 `config/rerank_config.py`:
```python
gpu_memory_utilization: float = 0.8
max_model_len: int = 10000
tensor_parallel_size: int = 1
enable_prefix_caching: bool = True
log_level: str = "WARNING"
```

**开发环境**
修改 `config/rerank_config.py`:
```python
gpu_memory_utilization: float = 0.3
max_model_len: int = 8000
port: int = 8891
log_level: str = "DEBUG"
```

**多GPU环境**
修改 `config/rerank_config.py`:
```python
tensor_parallel_size: int = 4
gpu_memory_utilization: float = 0.9
max_model_len: int = 10000
```

## API接口

### 端点列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务信息 |
| `/health` | GET | 健康检查 |
| `/v1/rerank` | POST | 重排序（标准） |
| `/rerank` | POST | 重排序（简化） |

### 详细说明

#### 1. GET `/health`

健康检查端点

**响应示例**
```json
{
  "status": "healthy",
  "model": "Qwen/Qwen3-Reranker-0.6B",
  "gpu_memory_utilization": 0.4,
  "max_model_len": 10000,
  "device": "cuda"
}
```

#### 2. POST `/v1/rerank`

对查询-文档对进行重排序

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pairs | array | ✓ | 查询-文档对列表 |
| instruction | string | ✗ | 任务指令 |
| model | string | ✗ | 模型名称（忽略） |

**QueryDocPair结构**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | ✓ | 查询文本 |
| document | string | ✓ | 文档文本 |

**请求示例**

基础用法：
```json
{
  "pairs": [
    {
      "query": "What is Python?",
      "document": "Python is a programming language."
    },
    {
      "query": "What is Python?",
      "document": "Java is also a programming language."
    }
  ]
}
```

带指令：
```json
{
  "pairs": [
    {
      "query": "机器学习",
      "document": "机器学习是人工智能的分支"
    }
  ],
  "instruction": "找出最相关的技术文档"
}
```

**响应格式**

```json
{
  "results": [
    {
      "index": 0,
      "score": 0.9876,
      "query": "What is Python?",
      "document": "Python is a programming language."
    },
    {
      "index": 1,
      "score": 0.4321,
      "query": "What is Python?",
      "document": "Java is also a programming language."
    }
  ],
  "model": "Qwen/Qwen3-Reranker-0.6B",
  "processing_time": 0.125
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| results | array | 重排序结果列表 |
| results[].index | integer | 原始索引位置 |
| results[].score | float | 相关性分数(0-1) |
| results[].query | string | 查询文本 |
| results[].document | string | 文档文本 |
| model | string | 模型名称 |
| processing_time | float | 处理时间（秒） |

**分数解释**

- **0.8 - 1.0**: 高度相关，强烈推荐
- **0.5 - 0.8**: 中度相关，可能相关
- **0.0 - 0.5**: 低度相关，不太相关

**状态码**

- `200`: 成功
- `400`: 请求参数错误
- `500`: 服务器内部错误
- `503`: 模型未加载

### 使用示例

#### Python

```python
import requests

# 基础用法
query = "Python编程"
documents = [
    "Python是一种编程语言",
    "Java是一种编程语言",
    "机器学习很流行"
]

pairs = [{"query": query, "document": doc} for doc in documents]
response = requests.post(
    "http://localhost:8891/v1/rerank",
    json={"pairs": pairs}
)

# 获取并排序结果
results = sorted(
    response.json()["results"],
    key=lambda x: x["score"],
    reverse=True
)

for i, r in enumerate(results, 1):
    print(f"{i}. Score: {r['score']:.4f} - {r['document']}")

# 带自定义指令
response = requests.post(
    "http://localhost:8891/v1/rerank",
    json={
        "pairs": pairs,
        "instruction": "检索与编程相关的文档"
    }
)

# 错误处理
try:
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.Timeout:
    print("请求超时")
except requests.exceptions.HTTPError as e:
    print(f"HTTP错误: {e.response.status_code}")
except Exception as e:
    print(f"错误: {e}")
```

#### JavaScript/Node.js

```javascript
const axios = require('axios');

// 重排序函数
async function rerankDocuments(query, documents) {
  const pairs = documents.map(doc => ({
    query: query,
    document: doc
  }));
  
  const response = await axios.post('http://localhost:8891/v1/rerank', {
    pairs: pairs
  });
  
  // 按分数排序
  return response.data.results.sort((a, b) => b.score - a.score);
}

// 使用示例
const query = "Python编程";
const documents = [
  "Python是一种编程语言",
  "Java是一种编程语言",
  "机器学习很流行"
];

rerankDocuments(query, documents)
  .then(results => {
    results.forEach((r, i) => {
      console.log(`${i+1}. Score: ${r.score.toFixed(4)} - ${r.document}`);
    });
  })
  .catch(error => console.error('Error:', error));
```

#### cURL

```bash
# 单个查询-文档对
curl -X POST http://localhost:8891/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "pairs": [
      {
        "query": "Python",
        "document": "Python is a programming language"
      }
    ]
  }'

# 批量重排序
curl -X POST http://localhost:8891/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "pairs": [
      {"query": "Python", "document": "Python是编程语言"},
      {"query": "Python", "document": "Java是编程语言"},
      {"query": "Python", "document": "机器学习很流行"}
    ],
    "instruction": "检索与Python相关的文档"
  }'
```

## 性能优化

### 性能指标

| 场景 | 批量大小 | 延迟 | 吞吐量 |
|------|---------|------|--------|
| 单对 | 1 | 100-200ms | 5-10 pairs/s |
| 小批量 | 10 | 400-600ms | 15-25 pairs/s |
| 大批量 | 32 | 1000-1500ms | 20-30 pairs/s |

*基于NVIDIA A100 GPU测试*

### 优化策略

#### 1. 批量处理

❌ **不推荐**
```python
for query, doc in pairs:
    response = requests.post(url, json={
        "pairs": [{"query": query, "document": doc}]
    })
```

✅ **推荐**
```python
pairs_list = [{"query": q, "document": d} for q, d in pairs]
response = requests.post(url, json={"pairs": pairs_list})
```

批量处理可以显著提高吞吐量。

#### 2. 启用前缀缓存

```python
# config/rerank_config.py
enable_prefix_caching: bool = True
```

前缀缓存可以减少重复计算，提高性能。

#### 3. GPU配置优化

修改 `config/rerank_config.py`:
```python
# 如果有足够显存，提高利用率
gpu_memory_utilization: float = 0.8

# 增加批处理大小
max_batch_size: int = 64
```

#### 4. 多GPU部署

修改 `config/rerank_config.py`:
```python
# 使用4个GPU
tensor_parallel_size: int = 4
```

#### 5. 多实例负载均衡

可以启动多个实例监听不同端口，需要创建多个配置文件或代码中动态修改。


### 性能监控

服务提供详细的性能日志：

```
INFO: Processing 32 query-document pairs for reranking
INFO: Reranked 32 pairs in 1.234s (25.9 pairs/s)
```

## 故障排除

### 常见问题

#### 1. CUDA out of memory

**症状**: `RuntimeError: CUDA out of memory`

**解决方法**:
```bash
# 降低显存使用率
export RERANK_GPU_MEMORY_UTILIZATION=0.3

# 减小最大长度
export RERANK_MAX_MODEL_LEN=8000

# 减小批处理大小
export RERANK_MAX_BATCH_SIZE=16
```

#### 2. 模型下载失败

**症状**: `OSError: Can't load tokenizer`

**解决方法**:
```bash
# 使用镜像
export HF_ENDPOINT=https://hf-mirror.com

# 或手动下载后使用本地路径
export RERANK_MODEL_PATH=/path/to/model
```

#### 3. 端口被占用

**症状**: `Address already in use`

**解决方法**:
```bash
# 更改端口
export RERANK_PORT=9001

# 或释放端口
lsof -ti:8891 | xargs kill -9
```

#### 4. 没有GPU

服务会自动降级到CPU模式，但性能较低（10-20倍慢）。

建议使用GPU或考虑使用云GPU服务。

#### 5. 分数异常

如果所有分数都很低或很高，检查：
- 查询和文档是否匹配
- 任务指令是否合适
- 输入是否被截断

### 日志分析

修改配置文件启用DEBUG日志查看详细信息：

```python
# config/rerank_config.py
log_level: str = "DEBUG"
```

```bash
python rerank_start.py
```

## 最佳实践

### 生产部署

#### 1. 使用进程管理器

**Systemd服务**

```ini
[Unit]
Description=Rerank Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/embedding_rerank
Environment="RERANK_GPU_MEMORY_UTILIZATION=0.7"
ExecStart=/usr/bin/python3 rerank_start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. 反向代理

**Nginx配置**

```nginx
upstream rerank_backend {
    server 127.0.0.1:8891;
    # 如有多实例
    # server 127.0.0.1:8892;
}

server {
    listen 80;
    server_name rerank.example.com;

    location / {
        proxy_pass http://rerank_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
```

#### 3. 容器化部署

**Dockerfile**

```dockerfile
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install vllm fastapi uvicorn transformers torch

COPY . /app
WORKDIR /app

EXPOSE 8891

CMD ["python3", "rerank_start.py"]
```

### 使用建议

#### 1. 合理设置批量大小

根据场景选择合适的批量大小：
- 实时场景：1-10
- 批量场景：20-50

#### 2. 预过滤候选文档

先用快速方法（如向量检索）筛选出top-k候选文档，再用Rerank精排序。

典型流程：
```
全部文档 (10000) 
  → 向量检索 (top-100) 
  → Rerank精排 (top-10)
```

#### 3. 缓存策略

对常见查询的结果进行缓存，减少重复计算。

#### 4. 监控和告警

- 监控延迟、吞吐量
- 监控GPU使用率
- 设置性能告警阈值

## 更新日志

### v1.0.0 (2026-02-03)

- ✅ 初始版本发布
- ✅ 支持Qwen3-Reranker-0.6B模型
- ✅ RESTful API接口
- ✅ 批量处理支持
- ✅ 前缀缓存优化
- ✅ 健康检查端点
- ✅ 完整的配置系统
- ✅ 生产级错误处理

## 相关文档

- **快速开始**: [RerankQUICKSTART.md](RerankQUICKSTART.md)
- **API参考**: [RerankAPI.md](RerankAPI.md)

## 许可证

本项目遵循Qwen模型的许可证条款。

## 技术支持

如有问题，请查阅：
1. 本文档的[故障排除](#故障排除)部分
2. [API文档](RerankAPI.md)
3. [快速开始指南](RerankQUICKSTART.md)
