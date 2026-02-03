# Embedding Service - 完整文档

基于vLLM和Qwen3-Embedding-0.6B的高性能向量化服务

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

Embedding Service是一个生产级的文本向量化服务，提供：

### 核心特性

- 🚀 **高性能推理**: 基于vLLM引擎，支持GPU加速
- 📦 **批量处理**: 高效的批量向量化
- 🔧 **灵活配置**: 支持环境变量和配置文件
- 🌐 **标准API**: 兼容OpenAI Embeddings API格式
- 📊 **完整监控**: 详细的日志和性能指标
- 🔄 **生产就绪**: 健康检查、优雅关闭等

### 技术栈

- **推理引擎**: vLLM 0.8.5+
- **模型**: Qwen3-Embedding-0.6B
- **框架**: FastAPI + Uvicorn
- **配置**: Pydantic
- **语言**: Python 3.8+

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

直接编辑配置文件 `config/embedding_config.py` 进行配置：

```bash
nano config/embedding_config.py
```

### 3. 启动

```bash
python embedding_start.py
```

启动成功后，服务将在 `http://0.0.0.0:8890` 运行。

### 4. 验证

```bash
# 健康检查
curl http://localhost:8890/health

# 生成向量
curl -X POST http://localhost:8890/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": ["Hello, world!"]}'
```

## 配置说明

### 配置方式

请直接修改 `config/embedding_config.py` 文件中的 `EmbeddingConfig` 类属性。

### 完整配置选项

#### 模型配置

```python
# 模型名称（HuggingFace模型ID）
model_name: str = "Qwen/Qwen3-Embedding-0.6B"

# 本地模型路径（可选，优先于model_name）
model_path: Optional[str] = None
```

#### GPU配置

```python
# GPU内存使用率 (0.0-1.0)
gpu_memory_utilization: float = 0.4

# 最大输入长度（tokens）
max_model_len: int = 3072

# 张量并行大小（GPU数量）
tensor_parallel_size: int = 1

# 数据类型
dtype: str = "float16"  # 可选: float16, bfloat16, float32
```

#### 服务配置

```python
# 监听地址
host: str = "0.0.0.0"

# 服务端口
port: int = 8890

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
修改 `config/embedding_config.py`:
```python
gpu_memory_utilization: float = 0.8
max_model_len: int = 3072
tensor_parallel_size: int = 1
log_level: str = "WARNING"
```

**开发环境**
修改 `config/embedding_config.py`:
```python
gpu_memory_utilization: float = 0.3
max_model_len: int = 2048
port: int = 8890
log_level: str = "DEBUG"
```

**多GPU环境**
修改 `config/embedding_config.py`:
```python
tensor_parallel_size: int = 4
gpu_memory_utilization: float = 0.9
max_model_len: int = 3072
```

## API接口

### 端点列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务信息 |
| `/health` | GET | 健康检查 |
| `/v1/embeddings` | POST | 生成向量（标准） |
| `/embeddings` | POST | 生成向量（简化） |

### 详细说明

#### 1. GET `/health`

健康检查端点

**响应示例**
```json
{
  "status": "healthy",
  "model": "Qwen/Qwen3-Embedding-0.6B",
  "gpu_memory_utilization": 0.4,
  "max_model_len": 3072,
  "device": "cuda"
}
```

#### 2. POST `/v1/embeddings`

生成文本向量

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| input | string/array | ✓ | 输入文本 |
| instruction | string | ✗ | 任务指令 |
| model | string | ✗ | 模型名称（忽略） |

**请求示例**

单个文本：
```json
{
  "input": "What is the capital of China?"
}
```

批量文本：
```json
{
  "input": [
    "What is the capital of China?",
    "Explain gravity"
  ]
}
```

带指令：
```json
{
  "input": ["Query text"],
  "instruction": "Given a web search query, retrieve relevant passages"
}
```

**响应格式**

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
response = requests.post(
    "http://localhost:8890/v1/embeddings",
    json={"input": "Hello, world!"}
)
data = response.json()
embedding = data["data"][0]["embedding"]

# 批量处理
texts = ["Text 1", "Text 2", "Text 3"]
response = requests.post(
    "http://localhost:8890/v1/embeddings",
    json={"input": texts}
)
embeddings = [d["embedding"] for d in response.json()["data"]]

# 带指令
response = requests.post(
    "http://localhost:8890/v1/embeddings",
    json={
        "input": ["Query: Machine learning"],
        "instruction": "Represent this sentence for searching relevant passages"
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

// 基础用法
async function getEmbedding(text) {
  const response = await axios.post('http://localhost:8890/v1/embeddings', {
    input: text
  });
  return response.data.data[0].embedding;
}

// 批量处理
async function getBatchEmbeddings(texts) {
  const response = await axios.post('http://localhost:8890/v1/embeddings', {
    input: texts
  });
  return response.data.data.map(d => d.embedding);
}

// 使用
const embedding = await getEmbedding("Hello, world!");
const embeddings = await getBatchEmbeddings(["Text 1", "Text 2"]);
```

#### cURL

```bash
# 单个文本
curl -X POST http://localhost:8890/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, world!"}'

# 批量文本
curl -X POST http://localhost:8890/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": ["Text 1", "Text 2", "Text 3"]}'

# 带指令
curl -X POST http://localhost:8890/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": ["Query text"],
    "instruction": "Represent for retrieval"
  }'
```

## 性能优化

### 性能指标

| 场景 | 批量大小 | 延迟 | 吞吐量 |
|------|---------|------|--------|
| 单个文本 | 1 | 50-100ms | 10-20 texts/s |
| 小批量 | 10 | 150-250ms | 40-60 texts/s |
| 大批量 | 32 | 400-600ms | 50-80 texts/s |

*基于NVIDIA A100 GPU测试*

### 优化策略

#### 1. 批量处理

❌ **不推荐**
```python
for text in texts:
    response = requests.post(url, json={"input": text})
```

✅ **推荐**
```python
response = requests.post(url, json={"input": texts})
```

批量处理可以提高吞吐量5-10倍。

#### 2. 连接复用

```python
import requests

session = requests.Session()
session.headers.update({"Content-Type": "application/json"})

for batch in batches:
    response = session.post(url, json={"input": batch})
```

#### 3. GPU配置优化

修改 `config/embedding_config.py`:
```python
# 如果有足够显存，提高利用率
gpu_memory_utilization: float = 0.8

# 增加批处理大小
max_batch_size: int = 64
```

#### 4. 多GPU部署

修改 `config/embedding_config.py`:
```python
# 使用4个GPU
tensor_parallel_size: int = 4
```

#### 5. 多实例负载均衡

可以启动多个实例监听不同端口，需要创建多个配置文件或代码中动态修改。


### 性能监控

服务提供详细的性能日志：

```
INFO: Processing 32 texts for embedding
INFO: Generated 32 embeddings in 0.523s (61.2 texts/s)
```

## 故障排除

### 常见问题

#### 1. CUDA out of memory

**症状**: `RuntimeError: CUDA out of memory`

**解决方法**:
修改 `config/embedding_config.py`:
```python
# 降低显存使用率
gpu_memory_utilization: float = 0.3

# 减小最大长度
max_model_len: int = 2048

# 减小批处理大小
max_batch_size: int = 16
```

#### 2. 模型下载失败

**症状**: `OSError: Can't load tokenizer`

**解决方法**:
```bash
# 使用镜像
export HF_ENDPOINT=https://hf-mirror.com
```
或修改 `config/embedding_config.py` 使用本地路径:
```python
model_path: str = "/path/to/model"
```

#### 3. 端口被占用

**症状**: `Address already in use`

**解决方法**:
修改 `config/embedding_config.py`:
```python
# 更改端口
port: int = 9000
```

或释放端口:
```bash
lsof -ti:8890 | xargs kill -9
```

#### 4. 没有GPU

服务会自动降级到CPU模式，但性能较低。

建议使用GPU或考虑使用更轻量的模型。

#### 5. 向量维度不匹配

Qwen3-Embedding-0.6B输出维度为**1024**，确保下游任务使用相同维度。

### 日志分析

修改配置文件启用DEBUG日志查看详细信息：

```python
# config/embedding_config.py
log_level: str = "DEBUG"
```

```bash
python embedding_start.py
```

## 最佳实践

### 生产部署

#### 1. 使用进程管理器

**Systemd服务**

```ini
[Unit]
Description=Embedding Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/embedding_rerank
Environment="EMBEDDING_GPU_MEMORY_UTILIZATION=0.7"
ExecStart=/usr/bin/python3 embedding_start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. 反向代理

**Nginx配置**

```nginx
upstream embedding_backend {
    server 127.0.0.1:8890;
    # 如有多实例
    # server 127.0.0.1:8891;
}

server {
    listen 80;
    server_name embedding.example.com;

    location / {
        proxy_pass http://embedding_backend;
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

EXPOSE 8890

CMD ["python3", "embedding_start.py"]
```

### 安全建议

1. **API认证**: 添加API密钥验证
2. **速率限制**: 防止滥用
3. **输入验证**: 限制输入长度
4. **HTTPS**: 使用SSL/TLS加密
5. **防火墙**: 限制访问IP

### 监控建议

1. **健康检查**: 定期调用`/health`端点
2. **性能监控**: 记录延迟、吞吐量
3. **资源监控**: GPU/CPU/内存使用率
4. **日志收集**: 集中化日志管理
5. **告警**: 异常情况及时通知

## 更新日志

### v1.0.0 (2026-02-03)

- ✅ 初始版本发布
- ✅ 支持Qwen3-Embedding-0.6B模型
- ✅ 兼容OpenAI Embeddings API
- ✅ 批量处理支持
- ✅ 健康检查端点
- ✅ 完整的配置系统
- ✅ 生产级错误处理

## 相关文档

- **快速开始**: [EmbeddingQUICKSTART.md](EmbeddingQUICKSTART.md)
- **API参考**: [EmbeddingAPI.md](EmbeddingAPI.md)

## 许可证

本项目遵循Qwen模型的许可证条款。

## 技术支持

如有问题，请查阅：
1. 本文档的[故障排除](#故障排除)部分
2. [API文档](EmbeddingAPI.md)
3. [快速开始指南](EmbeddingQUICKSTART.md)
