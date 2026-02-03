# Embedding Service - 快速开始

> 5分钟快速启动 Embedding 向量化服务

## 📋 前置要求

- Python 3.8+
- CUDA 11.8+ (使用GPU时)
- 4GB+ GPU显存 (推荐)

## 🚀 快速启动

### 1. 安装依赖

```bash
pip install vllm>=0.8.5 fastapi uvicorn transformers torch pydantic
```

### 2. 配置（可选）

如果需要修改端口、模型路径或GPU设置，请直接编辑配置文件：

```bash
nano config/embedding_config.py
```

### 3. 启动服务

```bash
python embedding_start.py
```

服务将在 **http://0.0.0.0:8890** 启动

### 3. 验证服务

```bash
# 健康检查
curl http://localhost:8890/health

# 生成向量
curl -X POST http://localhost:8890/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": ["Hello, world!"]}'
```

## ⚙️ 配置选项

### 配置文件

所有配置均在 `config/embedding_config.py` 中直接修改。

```python
class EmbeddingConfig(BaseModel):
    # 模型配置
    model_name: str = "Qwen/Qwen3-Embedding-0.6B"
    model_path: Optional[str] = None  # 可选：本地模型路径

    # GPU配置
    gpu_memory_utilization: float = 0.4
    max_model_len: int = 3072
    tensor_parallel_size: int = 1
    
    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8890
    ...
```

### 常用配置示例

**多GPU部署**
修改 `config/embedding_config.py`:
```python
tensor_parallel_size: int = 2
```

**低显存模式**
修改 `config/embedding_config.py`:
```python
gpu_memory_utilization: float = 0.3
max_model_len: int = 2048
```

**自定义端口**
修改 `config/embedding_config.py`:
```python
port: int = 9000
```

## 📝 使用示例

### Python客户端

```python
import requests

# 单个文本
response = requests.post(
    "http://localhost:8890/v1/embeddings",
    json={"input": "Hello, world!"}
)
embedding = response.json()["data"][0]["embedding"]

# 批量文本
response = requests.post(
    "http://localhost:8890/v1/embeddings",
    json={
        "input": [
            "What is the capital of China?",
            "Explain gravity"
        ]
    }
)
embeddings = [d["embedding"] for d in response.json()["data"]]

# 带任务指令
response = requests.post(
    "http://localhost:8890/v1/embeddings",
    json={
        "input": ["Query text"],
        "instruction": "Given a web search query, retrieve relevant passages"
    }
)
```

### cURL命令

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
    "instruction": "Retrieve relevant passages"
  }'
```

## 🧪 测试服务

```bash
# 运行测试套件
python test/test_embedding_service.py
```

## 🔧 常见问题

### Q: 显存不足怎么办？

修改 `config/embedding_config.py`，降低显存使用率或减小模型长度：
```python
gpu_memory_utilization: float = 0.3
max_model_len: int = 2048
```

### Q: 如何使用多GPU？

修改 `config/embedding_config.py`，设置张量并行大小：
```python
tensor_parallel_size: int = 2  # 使用2个GPU
```

### Q: 模型下载慢或失败？

使用镜像站点（设置环境变量）：
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

或使用本地模型，修改 `config/embedding_config.py`：
```python
model_path: str = "/path/to/local/model"
```

### Q: 如何提高性能？

1. **批量处理**: 一次发送多个文本
2. **提高显存**: 增加 `GPU_MEMORY_UTILIZATION`
3. **连接复用**: 使用 `requests.Session()`

## 📚 更多文档

- **完整文档**: [EmbeddingREADME.md](EmbeddingREADME.md)
- **API文档**: [EmbeddingAPI.md](EmbeddingAPI.md)
- **项目总览**: [README.md](README.md)

## 💡 最佳实践

### 批量处理

❌ **不推荐**
```python
for text in texts:
    response = requests.post(url, json={"input": text})
```

✅ **推荐**
```python
response = requests.post(url, json={"input": texts})
```

### 连接复用

```python
import requests

session = requests.Session()
for batch in batches:
    response = session.post(url, json={"input": batch})
```

## 🎯 下一步

- 查看 [EmbeddingAPI.md](EmbeddingAPI.md) 了解API端点详情
- 阅读 [EmbeddingREADME.md](EmbeddingREADME.md) 了解高级配置和优化
