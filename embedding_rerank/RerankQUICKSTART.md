# Rerank Service - 快速开始

> 5分钟快速启动 Rerank 重排序服务

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
nano config/rerank_config.py
```

### 3. 启动服务

```bash
python rerank_start.py
```

服务将在 **http://0.0.0.0:8891** 启动

### 3. 验证服务

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

## ⚙️ 配置选项

### 配置文件

所有配置均在 `config/rerank_config.py` 中直接修改。

```python
class RerankConfig(BaseModel):
    # 模型配置
    model_name: str = "Qwen/Qwen3-Reranker-0.6B"
    model_path: Optional[str] = None  # 可选：本地模型路径

    # GPU配置
    gpu_memory_utilization: float = 0.4
    max_model_len: int = 10000
    tensor_parallel_size: int = 1
    
    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8891
    ...
```

### 常用配置示例

**多GPU部署**
修改 `config/rerank_config.py`:
```python
tensor_parallel_size: int = 2
```

**低显存模式**
修改 `config/rerank_config.py`:
```python
gpu_memory_utilization: float = 0.3
max_model_len: int = 8000
```

**自定义端口**
修改 `config/rerank_config.py`:
```python
port: int = 9001
```

## 📝 使用示例

### Python客户端

```python
import requests

# 基础用法
query = "什么是机器学习？"
documents = [
    "机器学习是人工智能的一个分支。",
    "深度学习是机器学习的子集。",
    "Python是一种编程语言。"
]

pairs = [{"query": query, "document": doc} for doc in documents]
response = requests.post(
    "http://localhost:8891/v1/rerank",
    json={"pairs": pairs}
)

# 获取结果并排序
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
        "instruction": "找出最相关的技术文档"
    }
)
```

### cURL命令

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

## 🧪 测试服务

```bash
# 运行测试套件
python test/test_rerank_service.py

```

## 🔧 常见问题

### Q: 显存不足怎么办？

修改 `config/rerank_config.py`，降低显存使用率或减小模型长度：
```python
gpu_memory_utilization: float = 0.3
max_model_len: int = 8000
```

### Q: 如何使用多GPU？

修改 `config/rerank_config.py`，设置张量并行大小：
```python
tensor_parallel_size: int = 2  # 使用2个GPU
```

### Q: 模型下载慢或失败？

使用镜像站点（设置环境变量）：
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

或使用本地模型，修改 `config/rerank_config.py`：
```python
model_path: str = "/path/to/local/model"
```

### Q: 如何提高性能？

1. **批量处理**: 一次发送多个查询-文档对
2. **启用缓存**: 保持 `ENABLE_PREFIX_CACHING=True`
3. **提高显存**: 增加 `GPU_MEMORY_UTILIZATION`

### Q: 分数的含义是什么？

分数范围0-1，表示文档与查询的相关性概率：
- **0.8-1.0**: 高度相关
- **0.5-0.8**: 中度相关
- **0.0-0.5**: 低度相关

## 📚 更多文档

- **完整文档**: [RerankREADME.md](RerankREADME.md)
- **API文档**: [RerankAPI.md](RerankAPI.md)
- **项目总览**: [README.md](README.md)

## 💡 最佳实践

### 批量处理

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

### 错误处理

```python
import requests

try:
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    results = response.json()
except requests.exceptions.Timeout:
    print("请求超时")
except requests.exceptions.HTTPError as e:
    print(f"HTTP错误: {e.response.status_code}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 🎯 下一步

- 查看 [RerankAPI.md](RerankAPI.md) 了解API端点详情
- 阅读 [RerankREADME.md](RerankREADME.md) 了解高级配置和优化
