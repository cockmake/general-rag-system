# General RAG System

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![Spring Boot](https://img.shields.io/badge/Spring%20Boot-2.7.6-brightgreen)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-42b883)
![Python](https://img.shields.io/badge/Python-3.8+-3776ab)

**企业级 Agentic RAG 知识库问答系统**

支持多用户、多工作空间、智能代理检索、文档向量化等功能

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [系统架构](#-系统架构) • [配置指南](#-配置指南) • [Agentic RAG](#-agentic-rag-智能代理检索)

</div>

---

## 📖 项目简介

General RAG System 是一个基于**检索增强生成（Retrieval-Augmented Generation）**和**智能代理（Agentic AI）**技术的企业级知识库问答系统。通过将文档向量化存储，结合 LangGraph 状态机和大语言模型的决策能力，实现自主、精准、可靠的智能问答服务。

### 核心优势

- 🤖 **Agentic RAG**：基于 LangGraph 的智能代理检索，自主决策、多轮迭代、动态优化
- 🎯 **精准检索**：5种检索工具（语义+关键词+文件探索+上下文补全），智能选择最优策略
- 🔄 **多轮优化**：支持最多5轮检索迭代，自动补全不连续文档片段
- 🤖 **多模型支持**：兼容 OpenAI、DeepSeek、通义千问、Gemini、Claude 等多种 LLM
- 👥 **多租户架构**：支持工作空间隔离，权限精细化管理
- 📚 **文档管理**：支持 PDF、TXT 等多种格式，自动解析和分块
- 💬 **对话管理**：会话持久化，上下文记忆，历史回溯
- 🔐 **安全可靠**：JWT 认证，数据加密，操作审计

## 🏗️ 系统架构

```
general-rag-system/
├── rag-client/          # 前端界面（Vue 3.5 + Vite 7.2 + Ant Design Vue 4.2）
├── rag-server/          # 业务后端（Spring Boot 2.7 + MyBatis Plus 3.5 + Java 11）
├── rag-llm/             # AI 服务（FastAPI + LangChain + LangGraph，端口 8888）
└── embedding_rerank/    # 本地向量化与重排序服务（vLLM 0.8.5+ + FastAPI，可选）
```

### 技术选型

| 模块 | 技术栈 | 端口 | 说明 |
|------|--------|------|------|
| **前端** | Vue 3.5、Vite 7.2、Ant Design Vue 4.2、Pinia 3.0 | 5173 | Hash 路由，localStorage 持久化 |
| **后端** | Spring Boot 2.7、MyBatis Plus 3.5、JWT、Java 11 | 8080 | RESTful API，/api 统一前缀 |
| **AI 服务** | FastAPI、LangChain、LangGraph、Pydantic | 8888 | root_path="/rag"，SSE 流式响应 |
| **向量化服务** | vLLM 0.8.5+、FastAPI、PyTorch、Qwen3 模型 | 8890/8891 | 本地 Embedding 与 Rerank（可选） |
| **向量数据库** | Milvus 2.6+ | 19530 | 按 kbId 创建集合，30min 自动释放 |
| **对象存储** | MinIO 8.x | 9000 | S3 兼容，文档文件存储 |
| **关系数据库** | MySQL 8.0+ | 3306 | 业务数据持久化，15+ 表 |
| **缓存** | Redis 6.x/7.x | 6379 | Session、Token、JWT 黑名单 |
| **消息队列** | RabbitMQ 3.x | 5672 | DirectExchange，异步任务处理 |

### 模块详细文档

📚 **各模块详细技术文档**：
- [rag-client 前端文档](./rag-client/README.md) - Vue 3 开发指南、页面路由、状态管理
- [rag-server 后端文档](./rag-server/README.md) - Spring Boot 配置、API 路由、MyBatis 使用
- [rag-llm AI 服务文档](./rag-llm/README.md) - Agentic RAG 实现、LLM 集成、RabbitMQ 消费者
- [embedding_rerank 本地向量化文档](./embedding_rerank/) - vLLM 部署、性能调优

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

- 🤖 **Agentic RAG（智能代理检索）**
  - **自主决策检索策略**：基于 LangGraph 状态机，LLM 自主选择最优检索工具
  - **5种检索工具**：
    1. `search_by_grep` - 关键词精确检索（支持全库/单文件/多文件）
    2. `search_by_document_and_chunk_range` - 按文档ID获取chunk范围
    3. `search_by_filename_and_chunk_range` - 按文件名获取chunk范围
    4. `search_by_multi_queries_in_database` - 多角度语义检索+Rerank
    5. `list_filename_by_like` - 文件名模糊匹配列表
  - **多轮迭代优化**：支持最多5轮检索，自动补全上下文
  - **智能停止机制**：检索到足够信息后自动停止，节省资源
  - **实时过程反馈**：检索过程、工具调用、决策理由实时流式输出

- 🔍 **智能检索**
  - **Agentic RAG**: 基于 LangGraph 的智能代理检索系统
    - 自主决策检索策略（5种工具自动选择）
    - 多轮迭代检索优化
    - 动态上下文补全
  - 语义相似度搜索（向量检索 + 自动关键词融合）
  - 关键词精确检索（grep风格，支持全库/单文件/多文件）
  - 混合检索与重排序（Rerank）优化
  - 智能文档分块与范围获取

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
| Java | **11**（必须） | 后端运行环境（不支持其他版本） |
| Python | 3.8+ | AI 服务运行环境 |
| Maven | 3.6+ | Java 项目构建工具 |
| Docker | 20+ | 依赖服务容器化（推荐）|
| GPU | 可选 | vLLM 本地向量化（embedding_rerank，推荐 4GB+ 显存）|

### 依赖服务部署

使用 Docker Compose 一键部署所有依赖服务（推荐）：

```bash
# 创建 docker-compose.yml 后执行
docker-compose up -d
```

或手动安装：
- **MySQL 8.0+** - 业务数据库
- **Redis 6.x/7.x** - 缓存、Session、JWT 黑名单
- **Milvus 2.6+** - 向量数据库（需配置认证）
- **MinIO Latest** - 对象存储（S3 兼容）
- **RabbitMQ 3.x** - 消息队列（需配置用户名密码）

### 配置文件

⚠️ **重要：配置敏感信息**

本项目的配置文件包含敏感信息（API 密钥、数据库密码等），已被 `.gitignore` 排除。您需要手动创建配置文件：

#### 1. 后端配置（rag-server）

```bash
cd rag-server/src/main/resources
# 编辑 application-dev.yml，填入真实的：
# - MySQL 连接信息（端口 3306）
# - JWT 密钥（至少 32 字符，可用 openssl rand -base64 32 生成）
# - MinIO 访问密钥（endpoint, access-key, secret-key）
# - Redis 密码（端口 6379）
# - RabbitMQ 凭据（端口 5672）
# - Milvus 认证信息（uri, token）
```

📖 详细配置说明：[rag-server/README.md](./rag-server/README.md)

#### 2. AI 服务配置（rag-llm）

```bash
cd rag-llm
# 1. 编辑 model_config.json（参考 model_config.json.example）
# 填入各 LLM 的 API Key：
# - OpenAI (gpt-5.2, gpt-5.2-codex)
# - DeepSeek (deepseek-chat, deepseek-reasoner)
# - 通义千问 (qwen3-max, text-embedding-v4)
# - Gemini (gemini-3-flash-preview)
# - Claude (claude-4.5-sonnet)
# - 其他模型服务

# 2. 编辑 main.py 中的基础设施连接配置（约第 30-40 行）：
# - RabbitMQ 连接信息（host, port, username, password）
# - MinIO 访问密钥（endpoint, access-key, secret-key）
# - Milvus 认证令牌（uri, token）
# 生产环境建议使用环境变量替代硬编码
```

⚠️ **注意**：
- `model_config.json` 不要提交到 Git
- `main.py` 中的基础设施配置为硬编码，生产环境需修改或使用环境变量

📖 详细配置说明：[rag-llm/README.md](./rag-llm/README.md)

📚 **安全配置指南**：[SECURITY.md](./SECURITY.md)

### 启动服务

#### 1. 启动前端（端口 5173）

```bash
cd rag-client
npm install
npm run dev
# 访问 http://localhost:5173
```

📖 详细配置请参考：[rag-client/README.md](./rag-client/README.md)

#### 2. 启动后端（端口 8080，context-path /api）

```bash
cd rag-server
# 编辑 src/main/resources/application-dev.yml 配置数据库等信息
mvn clean install
mvn spring-boot:run
# 后端运行在 http://localhost:8080/api
```

⚠️ **注意**：必须使用 Java 11（不支持其他版本）

📖 详细配置请参考：[rag-server/README.md](./rag-server/README.md)

#### 3. 启动 LLM 服务（端口 8888，root_path /rag）

```bash
cd rag-llm
# 编辑 model_config.json 配置各 LLM 的 API Key
# 编辑 main.py 中的 RabbitMQ、MinIO、Milvus 连接信息
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8888 --workers 2
# LLM 服务运行在 http://localhost:8888
```

📖 详细配置请参考：[rag-llm/README.md](./rag-llm/README.md)

#### 4. 启动本地向量化服务（可选，需 GPU）

如果需要使用本地向量化和重排序服务（不依赖外部 API），需要 GPU 支持：

```bash
cd embedding_rerank

# 启动 Embedding 服务（端口 8890）
python embedding_start.py

# 启动 Rerank 服务（端口 8891）
python rerank_start.py
```

**系统要求**：
- GPU: NVIDIA GPU（推荐 4GB+ 显存，最佳 8GB+）
- CUDA: 11.8+
- Python: 3.8+
- vLLM: 0.8.5+

📖 详细配置请参考：
- [Embedding 服务文档](./embedding_rerank/EmbeddingREADME.md)
- [Rerank 服务文档](./embedding_rerank/RerankREADME.md)

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
├── rag-client/                      # 前端项目（Vue 3.5 + Vite 7.2）
│   ├── src/
│   │   ├── api/                     # API 接口封装（chatApi, kbApi, workspaceApi 等）
│   │   ├── stores/                  # Pinia 状态管理（user, theme, search, workspace, kb）
│   │   ├── router/                  # 路由配置（beforeEach 认证守卫）
│   │   ├── views/                   # 页面组件
│   │   │   ├── Login.vue            # 登录页
│   │   │   ├── Register.vue         # 注册页
│   │   │   ├── Dashboard.vue        # 仪表盘
│   │   │   ├── SearchSessions.vue   # 搜索会话
│   │   │   ├── chat/                # 对话页面（NewChat, ChatSession）
│   │   │   ├── kb/                  # 知识库页面（KnowledgeBases, KnowledgeDetails）
│   │   │   └── workspace/           # 工作空间页面（WorkspaceManagement）
│   │   ├── components/              # 公共组件（ChatMessage, DocumentList 等）
│   │   ├── layouts/                 # 布局组件（MainLayout）
│   │   ├── utils/                   # 工具函数（auth, markdown, format）
│   │   └── consts.js                # 常量定义（API_BASE_URL）
│   ├── package.json
│   ├── vite.config.js
│   └── README.md                    # 前端详细文档
│
├── rag-server/                      # 后端项目（Spring Boot 2.7 + Java 11）
│   ├── src/main/java/com/rag/ragserver/
│   │   ├── controller/              # 9 个 REST 控制器
│   │   │   ├── UserController.java
│   │   │   ├── WorkspaceController.java
│   │   │   ├── KbController.java
│   │   │   ├── ChatController.java
│   │   │   ├── QuerySessionController.java
│   │   │   ├── DashboardController.java
│   │   │   ├── ModelsController.java
│   │   │   ├── AuditLogsController.java
│   │   │   └── NotificationsController.java
│   │   ├── service/                 # 业务逻辑（接口 + impl/）
│   │   ├── mapper/                  # 15 个 MyBatis Mapper 接口
│   │   ├── domain/                  # 实体类 + VO 包
│   │   ├── dto/                     # 请求/响应 DTO
│   │   ├── configuration/           # Spring 配置类（CORS, JWT, MyBatis, Milvus 等）
│   │   ├── interceptor/             # JWT 拦截器（excludes /users/*）
│   │   ├── aspect/                  # AOP 切面（审计日志）
│   │   ├── exception/               # 全局异常处理
│   │   ├── rabbit/                  # RabbitMQ 消费者
│   │   ├── assembler/               # 对象转换器
│   │   └── utils/                   # 工具类
│   ├── src/main/resources/
│   │   ├── application.yml          # 主配置（port 8080, context-path /api）
│   │   ├── application-dev.yml      # 开发环境配置
│   │   ├── application-prod.yml     # 生产环境配置
│   │   └── com/rag/ragserver/mapper/  # ⚠️ MyBatis XML 映射文件（15 个）
│   ├── pom.xml
│   └── README.md                    # 后端详细文档
│
├── rag-llm/                         # LLM 服务（FastAPI，端口 8888）
│   ├── services/
│   │   └── chat.py                  # 聊天服务路由（/chat）
│   ├── mq/                          # RabbitMQ 消息队列
│   │   ├── connection.py            # 连接管理
│   │   ├── document_embedding.py    # 文档向量化消费者
│   │   └── session_name.py          # 会话名称生成消费者
│   ├── agentic_rag_controller.py    # LangGraph 状态机控制器（max 5 轮）
│   ├── agentic_rag_toolkit.py       # 5 种检索工具 + PROMPT
│   ├── agentic_rag_utils.py         # Agentic RAG 核心服务
│   ├── main.py                      # FastAPI 入口（root_path="/rag"）
│   ├── dependencies.py              # Lifespan 管理（RabbitMQ、Milvus 初始化）
│   ├── rag_utils.py                 # 传统 RAG 工具函数
│   ├── milvus_utils.py              # Milvus 操作（MilvusClientManager，30min 自动释放）
│   ├── minio_utils.py               # MinIO 对象存储操作
│   ├── utils.py                     # 通用工具（LLM 初始化、模型配置加载）
│   ├── openai_utils.py              # OpenAI API 封装
│   ├── gemini_utils.py              # Gemini API 封装
│   ├── requirements.txt             # Python 依赖
│   ├── model_config.json.example    # 模型配置模板
│   └── README.md                    # AI 服务详细文档
│
├── embedding_rerank/                # 本地向量化与重排序服务（可选）
│   ├── service/                     # 服务实现
│   │   ├── embedding_service.py     # Embedding 服务（Qwen3-Embedding-0.6B）
│   │   └── rerank_service.py        # Rerank 服务（Qwen3-Reranker-0.6B）
│   ├── config/                      # 配置模块
│   │   ├── embedding_config.py
│   │   └── rerank_config.py
│   ├── test/                        # 测试套件
│   ├── embedding_start.py           # Embedding 启动入口（端口 8890）
│   ├── rerank_start.py              # Rerank 启动入口（端口 8891）
│   ├── EmbeddingREADME.md          # Embedding 完整文档
│   ├── RerankREADME.md             # Rerank 完整文档
│   └── ...（API 文档、快速开始）
│
├── 1_general_rag.sql                # 数据库初始化 SQL（15+ 表）
├── .gitignore                       # Git 忽略配置
├── README.md                        # 项目主文档（本文件）
├── SECURITY.md                      # 安全配置指南
├── CONTRIBUTING.md                  # 贡献指南
└── LICENSE                          # Apache 2.0 开源协议
```

</details>

📚 **各模块详细文档**：
- [rag-client/README.md](./rag-client/README.md) - 前端开发指南（页面路由、状态管理、API 通信）
- [rag-server/README.md](./rag-server/README.md) - 后端开发指南（API 路由、MyBatis 配置、JWT 认证）
- [rag-llm/README.md](./rag-llm/README.md) - AI 服务指南（Agentic RAG、LLM 集成、RabbitMQ 消费者）
- [embedding_rerank/](./embedding_rerank/) - 本地向量化服务（vLLM 部署、性能调优）

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

## 🧠 Agentic RAG 智能代理检索

### 什么是 Agentic RAG？

Agentic RAG 是本系统的核心检索引擎，基于 **LangGraph 状态机** 和 **大语言模型决策**，实现了自主、智能的文档检索系统。不同于传统的单次检索方式，Agentic RAG 能够：

- 🎯 **自主决策**：LLM 根据问题和检索历史，自动选择最优检索工具
- 🔄 **多轮迭代**：支持最多5轮检索，逐步完善检索结果
- 🧩 **上下文补全**：自动检测并补全不连续的文档片段
- 🛑 **智能停止**：检索到足够信息后自动停止，避免过度检索
- 📊 **过程可视化**：实时流式输出检索过程、工具调用、决策理由

### 5种检索工具

#### 1. search_by_grep - 关键词精确检索
**适用场景**：代码级精确搜索、查找方法/类/变量/配置项
- 支持全库检索、单文件检索、多文件检索
- 支持 AND/OR 匹配模式（默认OR）
- 精确匹配，无歧义，速度快

**示例**：
```python
# 全库查找 Redis 相关代码
search_by_grep(keywords=["Redis"], file_names=None)

# 在 config.py 中查找端口配置
search_by_grep(keywords=["port"], file_names=["config.py"])

# 在多个 controller 文件中查找 API 端点
search_by_grep(keywords=["@app.route", "POST"], 
               file_names=["user_controller.py", "auth_controller.py"])
```

#### 2 & 3. chunk_range 工具 - 文档片段获取
**适用场景**：补全上下文、扩展文档范围、绕过检索失败
- `search_by_document_and_chunk_range` - 按文档ID获取
- `search_by_filename_and_chunk_range` - 按文件名获取
- 解决语义检索和关键词检索都失效的情况

**示例**：
```python
# 补全不连续的chunk
search_by_document_and_chunk_range(document_id=123, start=1, end=9)

# 基于已知信息局部获取（检索失效时）
search_by_filename_and_chunk_range(file_name="README.md", start=0, end=5)
```

#### 4. search_by_multi_queries_in_database - 多角度语义检索
**适用场景**：概念理解、描述性问题、需要高质量语义匹配
- 多query并行检索 + Rerank精排
- 支持动态阈值过滤（grade_score_threshold: 0.3-0.6）
- K-Means聚类去噪

**示例**：
```python
# 理解Rerank机制
search_by_multi_queries_in_database(
    queries=["Rerank重排序机制", "文档相关性评分", "检索结果精排"],
    grade_query="RAG系统中的Rerank是如何工作的",
    grade_score_threshold=0.5,
    top_k=10
)
```

#### 5. list_filename_by_like - 文件探索
**适用场景**：不确定文件名、浏览文件列表、按模式查找
- 支持SQL LIKE语法（前缀、包含、目录匹配）
- 仅返回元信息（fileName、documentId、maxChunkIndex）
- 需配合 chunk_range 工具获取实际内容

**示例**：
```python
# 查找所有配置文件
list_filename_by_like(pattern="%config%", limit=30)
# 然后选择目标文件获取内容
search_by_filename_and_chunk_range(file_name="config.yaml", start=0, end=5)
```

### 工作流程

```
用户提问
   ↓
┌─────────────────────────────────────┐
│  Agentic RAG Controller (LangGraph) │
├─────────────────────────────────────┤
│  第1轮：决策检索策略                 │
│  ├─ 分析问题类型                     │
│  ├─ 选择工具（5选1）                 │
│  └─ 执行检索                         │
│                                     │
│  第2-5轮：迭代优化（如需）            │
│  ├─ 评估当前检索结果                 │
│  ├─ 决定继续/停止                    │
│  ├─ 补全上下文/换角度检索            │
│  └─ 更新检索历史                     │
│                                     │
│  构建上下文                          │
│  ├─ 合并检索结果                     │
│  ├─ 去重并排序                       │
│  └─ 格式化为上下文                   │
└─────────────────────────────────────┘
   ↓
生成回答（流式输出）
```

### 技术实现

- **状态机框架**：LangGraph（支持循环、条件分支、状态持久化）
- **决策模型**：支持所有 LLM（GPT、Claude、DeepSeek、Qwen、Gemini等）
- **结构化输出**：Pydantic 模型定义，确保决策格式正确
- **流式传输**：SSE（Server-Sent Events）实时推送检索过程
- **容错机制**：工具调用失败自动降级，最多5轮保底

### 优势对比

| 特性 | 传统RAG | Agentic RAG |
|------|---------|-------------|
| 检索策略 | 固定单一 | 自主选择（5种工具） |
| 检索轮次 | 单次 | 多轮迭代（最多5轮） |
| 上下文补全 | 不支持 | 自动补全不连续chunk |
| 工具组合 | 不支持 | 支持工具链式调用 |
| 过程透明 | 黑盒 | 实时流式输出 |
| 适应性 | 差 | 强（根据问题动态调整） |

### 配置说明

在 `agentic_rag_controller.py` 中可配置：
- `max_rounds`: 最大检索轮次（默认5）
- `grade_score_threshold`: Rerank分数阈值（默认0.4）
- `top_k`: 每轮检索返回数量（默认10）

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
<summary><b>Q: Agentic RAG 和传统 RAG 有什么区别？</b></summary>

A: 主要区别：
- **检索策略**：传统RAG单一固定，Agentic RAG自主选择5种工具
- **检索轮次**：传统RAG单次检索，Agentic RAG支持最多5轮迭代
- **上下文处理**：Agentic RAG自动补全不连续chunk，提供完整上下文
- **适应性**：Agentic RAG根据问题类型动态调整策略
- **透明度**：Agentic RAG实时展示检索过程和决策理由

推荐在复杂问答、代码搜索、多文档关联等场景使用 Agentic RAG。
</details>

<details>
<summary><b>Q: Agentic RAG 的5种工具如何选择？</b></summary>

A: LLM会根据问题类型自动选择：
- **结构化查找**（如"XXX方法在哪"）→ `search_by_grep`
- **概念理解**（如"什么是XXX"）→ `search_by_multi_queries_in_database`
- **文件探索**（如"有哪些配置文件"）→ `list_filename_by_like`
- **上下文补全**（检索到不连续chunk）→ `chunk_range` 工具
- **检索失效**（其他工具无法命中）→ `chunk_range` 兜底

系统会在每轮检索后评估结果，决定是否继续、使用哪个工具。
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
