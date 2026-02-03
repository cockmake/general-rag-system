# General RAG System

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![Spring Boot](https://img.shields.io/badge/Spring%20Boot-2.7.6-brightgreen)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-42b883)
![Python](https://img.shields.io/badge/Python-3.8+-3776ab)

**一个功能完整的企业级 RAG（检索增强生成）知识库问答系统**

支持多用户、多工作空间、文档向量化、智能问答等功能

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [系统架构](#-系统架构) • [配置指南](#-配置指南) • [部署文档](#-部署)

</div>

---

## 📖 项目简介

General RAG System 是一个基于检索增强生成（Retrieval-Augmented Generation）技术的企业级知识库问答系统。通过将文档向量化存储，结合大语言模型的生成能力，实现精准、可靠的智能问答服务。

### 核心优势

- 🎯 **精准检索**：基于向量相似度的语义检索，支持多路召回策略
- 🤖 **多模型支持**：兼容 OpenAI、DeepSeek、通义千问、Gemini 等多种 LLM
- 👥 **多租户架构**：支持工作空间隔离，权限精细化管理
- 📚 **文档管理**：支持 PDF、TXT 等多种格式，自动解析和分块
- 💬 **对话管理**：会话持久化，上下文记忆，历史回溯
- 🔐 **安全可靠**：JWT 认证，数据加密，操作审计

## 🏗️ 系统架构

```
general-rag-system/
├── rag-client/          # 前端界面（Vue 3 + Vite + Ant Design Vue）
├── rag-server/          # 业务后端（Spring Boot + MyBatis Plus）
├── rag-llm/             # AI服务（FastAPI + LangChain + LangGraph）
└── embedding_rerank/    # 本地向量化与重排序服务（vLLM + FastAPI）
    ├── service/         # 服务实现（Embedding & Rerank）
    ├── config/          # 配置模块
    └── test/            # 测试套件
```

### 技术选型

| 模块 | 技术栈 | 说明 |
|------|--------|------|
| **前端** | Vue 3、Vite、Ant Design Vue 4、Pinia | 响应式UI，支持深色模式 |
| **后端** | Spring Boot 2.7、MyBatis Plus、JWT | RESTful API，统一鉴权 |
| **AI服务** | FastAPI、LangChain、LangGraph | 异步处理，流式响应 |
| **向量化服务** | vLLM 0.8.5+、FastAPI、PyTorch | 本地Embedding与Rerank |
| **向量数据库** | Milvus 2.6+ | 高性能向量检索 |
| **对象存储** | MinIO 8.x | 文档文件存储 |
| **关系数据库** | MySQL 8.0+ | 业务数据持久化 |
| **缓存** | Redis 6.x | Session、Token缓存 |
| **消息队列** | RabbitMQ 3.x | 异步任务处理 |

### 系统架构图

```
┌─────────────┐
│  浏览器      │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐      ┌──────────────┐
│  rag-client │      │  rag-server  │
│  (Vue.js)   │◄────►│ (Spring Boot)│
└─────────────┘      └──────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌─────────────┐   ┌──────────────┐
│  rag-llm     │   │   MySQL     │   │   MinIO      │
│  (FastAPI)   │   │ (业务数据)   │   │ (文件存储)    │
└──────┬───────┘   └─────────────┘   └──────────────┘
       │
       ├──────────┬────────────┬──────────────┐
       ▼          ▼            ▼              ▼
┌──────────┐ ┌─────────┐ ┌─────────┐  ┌──────────┐
│  Milvus  │ │  Redis  │ │RabbitMQ │  │   LLM    │
│(向量检索) │ │ (缓存)  │ │ (队列)  │  │ API(s)   │
└──────────┘ └─────────┘ └─────────┘  └──────────┘
```

## ✨ 功能特性

### 核心功能

- 📄 **文档管理**
  - 支持 PDF、TXT、Markdown 等多种格式
  - 自动解析文档内容和结构
  - 智能分块（Chunk）和向量化
  - 文档版本管理和更新
  - MinIO 对象存储，支持大文件

- 🔍 **智能检索**
  - 语义相似度搜索
  - 混合检索（向量+关键词）
  - 重排序（Rerank）优化
  - Top-K 结果返回

- 💬 **对话问答**
  - 基于 RAG 的准确回答
  - 流式输出（SSE）
  - 多轮对话上下文
  - 引用来源标注

- 👥 **多租户管理**
  - 工作空间隔离
  - 成员权限控制
  - 知识库共享
  - 操作审计日志

- 🎨 **用户体验**
  - Markdown 渲染（markdown-it）
  - 代码高亮（highlight.js）
  - 数学公式支持（MathJax3）
  - 任务列表、Emoji 支持
  - 深色/浅色主题
  - 响应式布局

## 🚀 快速开始

### 前置要求

| 软件 | 版本要求 | 说明 |
|------|----------|------|
| Node.js | 18+ | 前端开发环境 |
| Java | 11 | 后端运行环境（必须11） |
| Python | 3.8+ | AI服务运行环境 |
| Maven | 3.6+ | Java项目构建工具 |
| Docker | 20+ | 依赖服务容器化（推荐）|
| GPU | 可选 | vLLM本地向量化需要（embedding_rerank）|

### 依赖服务部署

使用 Docker Compose 一键部署所有依赖服务（推荐）：

```bash
# 创建 docker-compose.yml 后执行
docker-compose up -d
```

或手动安装：
- MySQL 8.0+（推荐 8.0.x 或更高版本）
- Redis 6.x 或 7.x
- Milvus 2.6+（需要配置认证）
- MinIO（Latest）
- RabbitMQ 3.x（需配置用户名密码）

### 配置文件

⚠️ **重要：配置敏感信息**

本项目的配置文件包含敏感信息（API密钥、数据库密码等），已被 `.gitignore` 排除。您需要手动创建配置文件：

#### 1. 后端配置

```bash
# 复制配置模板
cd rag-server/src/main/resources
cp application-dev.yml.example application-dev.yml
cp application-prod.yml.example application-prod.yml

# 编辑配置文件，填入真实的：
# - 数据库连接信息
# - JWT 密钥（至少32位）
# - MinIO 访问密钥
# - Redis 密码
# - RabbitMQ 凭据
# - 邮箱配置
# - Milvus 认证信息
```

#### 2. LLM服务配置

```bash
# 复制配置模板
cd rag-llm
cp model_config.json.example model_config.json

# 编辑 model_config.json，填入各 AI 服务商的 API Key：
# - OpenAI / ChatGPT
# - DeepSeek
# - 通义千问（Qwen）
# - Gemini
# - 其他模型服务

# 注意：main.py 中包含基础设施连接配置：
# - RabbitMQ 连接信息
# - MinIO 访问密钥
# - Milvus 认证令牌
# 生产环境请修改这些硬编码配置或使用环境变量
```

📚 **详细配置说明请参考 [SECURITY.md](./SECURITY.md)**

### 启动服务

#### 1. 启动前端

```bash
cd rag-client
npm install
npm run dev
# 访问 http://localhost:5173
```

#### 2. 启动后端

```bash
cd rag-server
mvn clean install
mvn spring-boot:run
# 后端运行在 http://localhost:8080
```

#### 3. 启动 LLM 服务

```bash
cd rag-llm
pip install -r requirements.txt
# 使用 uvicorn 启动服务（推荐）
uvicorn main:app --host 0.0.0.0 --port 8888 --workers 2
# 或直接使用 python
python main.py
# LLM服务运行在 http://localhost:8888
```

#### 4. 启动本地向量化服务（可选）

如果需要使用本地向量化和重排序服务（不依赖外部API），需要GPU支持：

```bash
cd embedding_rerank

# 安装依赖
pip install vllm>=0.8.5 fastapi uvicorn[standard]

# 启动 Embedding 服务（默认端口: 8890）
python embedding_start.py

# 启动 Rerank 服务（默认端口: 8891）
python rerank_start.py
```

**系统要求**：
- GPU: NVIDIA GPU (推荐4GB+显存)
- CUDA: 11.8+
- Python: 3.8+
- vLLM: 0.8.5+

**模型说明**：
- **Embedding服务**: 使用 `Qwen/Qwen3-Embedding-0.6B` 模型进行文本向量化
- **Rerank服务**: 使用 `Qwen/Qwen3-Reranker-0.6B` 模型进行文档重排序

详细配置和使用说明请参考：
- [Embedding服务文档](./embedding_rerank/EmbeddingREADME.md)
- [Rerank服务文档](./embedding_rerank/RerankREADME.md)

### 数据库初始化

```sql
-- 创建数据库
CREATE DATABASE general_rag DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 导入表结构和初始数据
source 1_general_rag.sql
```

**说明**：`1_general_rag.sql` 文件位于项目根目录，包含完整的数据库表结构定义，包括：
- 用户表（users）
- 工作空间表（workspaces）
- 知识库表（knowledgebases）
- 文档表（documents）
- 会话表（conversations、conversation_messages）
- 审计日志表（audit_logs）
- 等更多表...

## 📁 项目结构

<details>
<summary>点击展开详细结构</summary>

```
general-rag-system/
├── rag-client/                      # 前端项目
│   ├── src/
│   │   ├── api/                     # API接口封装
│   │   ├── components/              # 公共组件
│   │   ├── views/                   # 页面视图
│   │   ├── router/                  # 路由配置
│   │   ├── stores/                  # 状态管理（Pinia）
│   │   └── utils/                   # 工具函数
│   ├── package.json
│   └── vite.config.js
│
├── rag-server/                      # 后端项目
│   ├── src/main/java/com/rag/ragserver/
│   │   ├── controller/              # 控制器
│   │   ├── service/                 # 业务逻辑
│   │   ├── mapper/                  # 数据访问
│   │   ├── domain/                  # 实体类
│   │   ├── configuration/           # 配置类
│   │   └── common/                  # 公共类
│   ├── src/main/resources/
│   │   ├── application.yml          # 主配置
│   │   ├── application-dev.yml.example   # 开发环境配置模板
│   │   ├── application-prod.yml.example  # 生产环境配置模板
│   │   └── com/rag/ragserver/mapper/     # MyBatis XML映射文件
│   └── pom.xml
│
├── rag-llm/                         # LLM服务（端口: 8888）
│   ├── services/                    # 业务服务
│   │   └── chat/                    # 聊天服务
│   ├── mq/                          # 消息队列处理
│   ├── main.py                      # 入口文件
│   ├── rag_utils.py                 # RAG工具函数
│   ├── milvus_utils.py              # Milvus操作
│   ├── minio_utils.py               # MinIO操作
│   ├── gemini_utils.py              # Gemini API集成
│   ├── openai_utils.py              # OpenAI API集成
│   ├── requirements.txt             # Python依赖
│   └── model_config.json.example    # 模型配置模板
│
├── embedding_rerank/                # 本地向量化与重排序服务
│   ├── service/                     # 服务实现
│   │   ├── embedding_service.py     # Embedding服务（Qwen3-Embedding-0.6B）
│   │   └── rerank_service.py        # Rerank服务（Qwen3-Reranker-0.6B）
│   ├── config/                      # 配置模块
│   │   ├── embedding_config.py      # Embedding配置
│   │   └── rerank_config.py         # Rerank配置
│   ├── test/                        # 测试套件
│   │   ├── test_embedding_service.py
│   │   └── test_rerank_service.py
│   ├── embedding_start.py           # Embedding服务启动入口
│   ├── rerank_start.py              # Rerank服务启动入口
│   ├── EmbeddingREADME.md          # Embedding服务完整文档
│   ├── EmbeddingQUICKSTART.md      # Embedding快速开始
│   ├── EmbeddingAPI.md             # Embedding API文档
│   ├── RerankREADME.md             # Rerank服务完整文档
│   ├── RerankQUICKSTART.md         # Rerank快速开始
│   └── RerankAPI.md                # Rerank API文档
│
├── 1_general_rag.sql                # 数据库初始化SQL
├── .gitignore                       # Git忽略配置
├── README.md                        # 项目说明（本文件）
├── SECURITY.md                      # 安全配置指南
├── CONTRIBUTING.md                  # 贡献指南
├── LICENSE                          # Apache 2.0 开源协议
└── CLEAN_GIT_HISTORY.md             # Git历史清理说明
```

</details>

## 🔧 配置指南

### 环境变量方式（推荐生产环境）

```bash
# 后端服务环境变量
export MYSQL_PASSWORD=your_password
export JWT_SECRET=your_jwt_secret_key
export MINIO_SECRET_KEY=your_minio_key
export REDIS_PASSWORD=your_redis_password

# LLM服务环境变量
export OPENAI_API_KEY=sk-xxxxx
export DEEPSEEK_API_KEY=sk-xxxxx
export QWEN_API_KEY=sk-xxxxx
```

### 密钥生成建议

```bash
# 生成32位JWT密钥
openssl rand -base64 32

# 生成强密码
openssl rand -base64 16
```

## 🐳 部署

### 本地向量化服务部署

`embedding_rerank` 模块提供了本地向量化和重排序能力，适合对数据隐私有高要求或希望降低API调用成本的场景。

#### 部署架构

```
┌─────────────────────────────────────────┐
│  General RAG System                     │
├─────────────────────────────────────────┤
│                                         │
│  rag-llm (8888)                        │
│    │                                    │
│    ├──► External LLM APIs              │
│    │    (OpenAI, DeepSeek, Qwen...)   │
│    │                                    │
│    └──► Local Services (Optional)      │
│         ├─► Embedding (8890)           │
│         │   Qwen3-Embedding-0.6B       │
│         └─► Rerank (8891)              │
│             Qwen3-Reranker-0.6B        │
└─────────────────────────────────────────┘
```

#### 快速部署

1. **确保GPU环境**

```bash
# 检查NVIDIA GPU
nvidia-smi

# 确认CUDA版本 (需要11.8+)
nvcc --version
```

2. **安装依赖**

```bash
cd embedding_rerank

# 安装核心依赖
pip install vllm>=0.8.5
pip install fastapi uvicorn[standard]
pip install pydantic pydantic-settings
```

3. **启动服务**

```bash
# 方式1：分别启动（推荐）
python embedding_start.py    # Terminal 1
python rerank_start.py        # Terminal 2

# 方式2：后台运行
nohup python embedding_start.py > embedding.log 2>&1 &
nohup python rerank_start.py > rerank.log 2>&1 &
```

4. **验证服务**

```bash
# 测试 Embedding 服务
curl http://localhost:8890/health

# 测试 Rerank 服务
curl http://localhost:8891/health
```

#### 配置说明

服务支持环境变量和配置文件两种方式：

```bash
# Embedding 服务配置
export EMBEDDING_MODEL_NAME="Qwen/Qwen3-Embedding-0.6B"
export EMBEDDING_PORT=8890
export EMBEDDING_GPU_MEMORY_UTILIZATION=0.4
export EMBEDDING_MAX_MODEL_LEN=3072

# Rerank 服务配置
export RERANK_MODEL_NAME="Qwen/Qwen3-Reranker-0.6B"
export RERANK_PORT=8891
export RERANK_GPU_MEMORY_UTILIZATION=0.4
export RERANK_MAX_MODEL_LEN=3072
```

详细文档：
- 📖 [Embedding服务完整指南](./embedding_rerank/EmbeddingREADME.md)
- 📖 [Rerank服务完整指南](./embedding_rerank/RerankREADME.md)
- 🚀 [快速开始](./embedding_rerank/EmbeddingQUICKSTART.md)
- 📡 [API文档](./embedding_rerank/EmbeddingAPI.md)

### Docker Compose 一键部署

基础设施服务Docker部署配置：

```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: your_password
      MYSQL_DATABASE: general_rag
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass your_password
    ports:
      - "6379:6379"

  milvus:
    image: milvusdb/milvus:v2.3.0
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
    ports:
      - "19530:19530"

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: your_password
    ports:
      - "9000:9000"
      - "9001:9001"

  rabbitmq:
    image: rabbitmq:3-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: your_password
    ports:
      - "5672:5672"
      - "15672:15672"

volumes:
  mysql_data:
```

启动命令：
```bash
docker-compose up -d
```

### 生产部署建议

1. **反向代理**：使用 Nginx 作为前端服务器和 API 网关
2. **负载均衡**：后端服务多实例部署
3. **数据备份**：定期备份 MySQL 和 Milvus 数据
4. **监控告警**：接入 Prometheus + Grafana
5. **日志收集**：ELK Stack 或云服务日志平台

## 📚 文档链接

- [前端开发文档](./rag-client/README.md) - Vue 3 开发指南
- [后端开发文档](./rag-server/README.md) - Spring Boot API 文档
- [LLM服务文档](./rag-llm/README.md) - FastAPI 服务说明
- **[Embedding服务文档](./embedding_rerank/EmbeddingREADME.md)** - 本地向量化服务指南
- **[Rerank服务文档](./embedding_rerank/RerankREADME.md)** - 本地重排序服务指南
- [安全配置指南](./SECURITY.md) - 敏感信息配置说明
- [贡献指南](./CONTRIBUTING.md) - 如何参与项目开发
- [Git历史清理](./CLEAN_GIT_HISTORY.md) - 仓库清理记录

## 📄 开源协议

本项目采用 [Apache License 2.0](./LICENSE) 协议开源。

### 主要权限

- ✅ 商业使用
- ✅ 修改和分发
- ✅ 专利授权
- ✅ 私有使用

### 主要限制

- ⚠️ 必须保留版权声明
- ⚠️ 必须声明修改内容
- ⚠️ 必须包含 LICENSE 副本
- ❌ 不提供责任担保

详细信息请参阅 [LICENSE](./LICENSE) 文件。

## 🤝 贡献指南

我们欢迎所有形式的贡献！在提交 Pull Request 之前，请：

1. 阅读我们的 [贡献指南](./CONTRIBUTING.md)
2. 确保代码符合项目规范
3. 添加必要的测试和文档
4. 遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范

### 快速开始贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add some amazing feature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 🙋 常见问题

<details>
<summary><b>Q: 如何选择合适的 LLM 模型？</b></summary>

A: 建议根据场景选择：
- 快速响应：GPT-3.5、DeepSeek-Chat、Qwen-Plus
- 高质量：GPT-4、Claude-3、Qwen-Max
- 成本优化：本地部署开源模型（LLaMA、ChatGLM）
</details>

<details>
<summary><b>Q: 向量数据库可以替换为其他方案吗？</b></summary>

A: 可以，本项目基于 LangChain，理论上支持：
- Milvus（当前方案，推荐）
- Pinecone、Weaviate、Qdrant
- Elasticsearch（需要修改部分代码）
</details>

<details>
<summary><b>Q: 支持哪些文档格式？</b></summary>

A: 当前支持：
- **PDF**（通过 PyMuPDF / pdfplumber）
- **TXT、MD**（纯文本、Markdown）
- 图片OCR（通过 Tesseract，需要额外安装）

可通过扩展 `rag_utils.py` 支持更多格式（Word、Excel、HTML等）
</details>

<details>
<summary><b>Q: LLM服务为什么运行在8888端口？</b></summary>

A: 这是在 `main.py` 中配置的，建议使用：
```bash
uvicorn main:app --host 0.0.0.0 --port 8888 --workers 2
```
可根据需要修改端口，但需同步更新 `rag-server` 中的配置。
</details>

<details>
<summary><b>Q: embedding_rerank 模块的作用是什么？</b></summary>

A: `embedding_rerank` 提供本地向量化和重排序服务，包含两个独立的微服务：

**Embedding 服务** (端口: 8890)
- 基于 Qwen3-Embedding-0.6B 模型
- 将文本转换为768维向量
- 支持批量向量化（最多1024条/次）
- 兼容 OpenAI Embeddings API 格式

**Rerank 服务** (端口: 8891)
- 基于 Qwen3-Reranker-0.6B 模型
- 对检索结果进行精确重排序
- 提高召回文档的相关性
- 支持批量重排序

**适用场景**：
- ✅ 对数据隐私有严格要求
- ✅ 希望降低外部API调用成本
- ✅ 有本地GPU资源（推荐4GB+显存）
- ✅ 需要完全离线部署

**技术栈**：
- vLLM 0.8.5+ (高性能推理引擎)
- FastAPI (异步Web框架)
- PyTorch (深度学习框架)

**性能参考**：
- Embedding: ~100条/秒 (单GPU, batch_size=32)
- Rerank: ~50对/秒 (单GPU, batch_size=16)

详见: [Embedding文档](./embedding_rerank/EmbeddingREADME.md) | [Rerank文档](./embedding_rerank/RerankREADME.md)
</details>

<details>
<summary><b>Q: 如何在 rag-llm 中使用本地向量化服务？</b></summary>

A: 配置 `rag-llm/main.py` 或使用环境变量：

```python
# 在 main.py 中配置
EMBEDDING_SERVICE_URL = "http://localhost:8890"
RERANK_SERVICE_URL = "http://localhost:8891"

# 或使用环境变量
export EMBEDDING_SERVICE_URL="http://localhost:8890"
export RERANK_SERVICE_URL="http://localhost:8891"
```

然后在 RAG 流程中调用本地服务替代外部API。
</details>

<details>
<summary><b>Q: 本地向量化服务需要什么硬件配置？</b></summary>

A: **最低配置**：
- GPU: NVIDIA GPU (4GB显存，如GTX 1650)
- CPU: 4核
- 内存: 8GB
- 硬盘: 10GB

**推荐配置**：
- GPU: NVIDIA GPU (8GB+显存，如RTX 3060)
- CPU: 8核+
- 内存: 16GB+
- 硬盘: 20GB+ SSD
- CUDA: 11.8+

**性能对比**：
- 4GB显存: 可运行，需调低 `gpu_memory_utilization`
- 8GB显存: 流畅运行，推荐配置
- 16GB+显存: 可同时运行多个服务或更大模型
</details>

## 📊 项目状态

![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/general-rag-system)
![GitHub issues](https://img.shields.io/github/issues/yourusername/general-rag-system)
![GitHub stars](https://img.shields.io/github/stars/yourusername/general-rag-system)

## 📧 联系方式

- 提交 Issue: [GitHub Issues](../../issues)
- 讨论交流: [GitHub Discussions](../../discussions)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star！**

Made with ❤️ by General RAG System Contributors

[Apache License 2.0](./LICENSE) © 2026

---

### 技术支持

- 📖 [完整文档](../../wiki)
- 💬 [常见问题](../../issues?q=label%3Aquestion)
- 🐛 [报告Bug](../../issues/new?template=bug_report.md)
- 💡 [功能建议](../../issues/new?template=feature_request.md)

</div>
