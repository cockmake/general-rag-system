# Embedding Service 快速开始指南

## 📦 安装

### 1. 安装Python依赖

```bash
cd embedding_rerank
pip install -r requirements.txt
```

**注意**：需要 Python 3.8+，推荐使用虚拟环境。

### 2. 配置环境变量（可选）

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，修改配置
# 大多数情况下使用默认配置即可
```

## 🚀 启动服务

### 方式一：使用Python直接启动

```bash
python start.py
```

### 方式二：使用启动脚本

**Linux/Mac:**
```bash
bash run.sh
```

**Windows:**
```cmd
run.bat
```

### 启动成功标志

看到以下输出说明服务启动成功：

```
======================================================================
Embedding Service Configuration:
======================================================================
Model: Qwen/Qwen3-Embedding-0.6B
GPU Memory Utilization: 0.4
Max Model Length: 3072
...
======================================================================
Embedding Service Ready!
======================================================================
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8890
```

## 🧪 测试服务

### 1. 运行自动化测试

```bash
python test_service.py
```

### 2. 手动测试

**健康检查:**
```bash
curl http://localhost:8890/health
```

**生成向量:**
```bash
curl -X POST http://localhost:8890/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "测试文本"}'
```

## 📊 常用配置

### 显存占用调整

默认占用 40% GPU 显存，如需调整：

```bash
# 方式1: 环境变量
export EMBEDDING_GPU_MEMORY_UTILIZATION=0.6

# 方式2: 修改 .env 文件
EMBEDDING_GPU_MEMORY_UTILIZATION=0.6
```

### 端口修改

```bash
# 环境变量
export EMBEDDING_PORT=9000

# 或修改 .env 文件
EMBEDDING_PORT=9000
```

### 更换模型

```bash
# 使用其他模型
export EMBEDDING_MODEL_NAME=BAAI/bge-large-zh-v1.5

# 或使用本地模型路径
export EMBEDDING_MODEL_PATH=/path/to/local/model
```

## 🔌 集成到 rag-llm

### 1. 修改 rag-llm 配置

在 `rag-llm/model_config.json` 中添加：

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

### 2. 使用本地Embedding

在 `rag-llm` 代码中：

```python
# 原来使用的配置
embedding_config = {
    'name': 'text-embedding-v4',
    'provider': 'qwen'
}

# 改为使用本地服务
embedding_config = {
    'name': 'text-embedding-0.6b',
    'provider': 'local'
}

embeddings = get_embedding_instance(embedding_config)
```

## 🐛 常见问题

### 1. 端口被占用

**错误**: `Address already in use`

**解决**:
```bash
# 检查端口占用
netstat -ano | findstr :8890  # Windows
lsof -i :8890                 # Linux/Mac

# 或者更换端口
export EMBEDDING_PORT=8891
```

### 2. 显存不足

**错误**: `CUDA out of memory`

**解决**:
```bash
# 降低显存占用
export EMBEDDING_GPU_MEMORY_UTILIZATION=0.3

# 或使用更小的模型
export EMBEDDING_MODEL_NAME=Qwen/Qwen3-Embedding-0.6B
```

### 3. 模型下载失败

**解决**:
```bash
# 方式1: 设置 HuggingFace 镜像
export HF_ENDPOINT=https://hf-mirror.com

# 方式2: 手动下载后使用本地路径
export EMBEDDING_MODEL_PATH=/path/to/downloaded/model
```

### 4. 没有GPU

服务可以在 CPU 上运行，但速度会很慢：

```bash
# CPU模式会自动检测，无需额外配置
# 但推荐使用更小的模型以提升速度
```

## 📈 性能优化建议

### 1. 批量处理

❌ **避免**：多次单个请求
```python
for text in texts:
    response = requests.post(url, json={"input": text})
```

✅ **推荐**：批量请求
```python
response = requests.post(url, json={"input": texts})
```

### 2. 提高显存利用率

如果有足够显存，可以提高利用率：

```bash
# 默认0.4，可以提高到0.8-0.9
export EMBEDDING_GPU_MEMORY_UTILIZATION=0.8
```

### 3. 使用连接池

```python
import requests

# 创建session复用连接
session = requests.Session()

# 多次请求复用连接
for batch in batches:
    response = session.post(url, json={"input": batch})
```

## 📚 更多文档

- [API 文档](API.md) - 完整的 API 接口说明
- [README](README.md) - 详细的功能介绍和架构说明
- [.env.example](.env.example) - 所有配置参数说明

## 🆘 获取帮助

如遇到问题：

1. 检查服务日志输出
2. 访问 `/health` 端点查看服务状态
3. 查看 [常见问题](#-常见问题) 章节
4. 参考 [API 文档](API.md) 了解详细用法

## 🎯 下一步

- [ ] 测试服务是否正常工作
- [ ] 集成到 rag-llm 项目
- [ ] 根据实际情况调整配置
- [ ] 部署到生产环境（可选）
