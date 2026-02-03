# General RAG System Copilot Instructions

## Project Overview

General RAG System is an enterprise-grade knowledge base Q&A system based on Retrieval-Augmented Generation technology. The system includes four main modules:

*   **`rag-client`**: Frontend application (Vue 3.5 + Vite 7.2 + Ant Design Vue 4.2)
*   **`rag-server`**: Backend business service (Spring Boot 2.7.6 + MyBatis Plus 3.5.15 + Java 11)
*   **`rag-llm`**: AI/ML service (Python 3.8+ + FastAPI + LangChain + LangGraph)
*   **`embedding_rerank`**: Local vectorization and reranking service (vLLM 0.8.5+ + Qwen3 models)

## Build and Run Commands

### Frontend (`rag-client`)
*   **Install dependencies**: `npm install`
*   **Start development server**: `npm run dev` (default port: 5173)
*   **Build for production**: `npm run build`
*   **Preview build**: `npm run preview`

### Backend (`rag-server`)
*   **Start application**: `mvn spring-boot:run` (default port: 8080)
*   **Clean and install**: `mvn clean install`
*   **Configuration**:
    *   Main config: `src/main/resources/application.yml`
    *   Environment overrides: `application-dev.yml`, `application-prod.yml`

### LLM Service (`rag-llm`)
*   **Install dependencies**: `pip install -r requirements.txt`
*   **Start server**: `uvicorn main:app --host 0.0.0.0 --port 8888 --workers 2`
    *   Note: The service runs on port 8888 by default, root_path="/rag"

### Embedding & Rerank Services (Optional)
*   **Embedding service**: `python embedding_rerank/embedding_start.py` (default port: 8890)
*   **Rerank service**: `python embedding_rerank/rerank_start.py` (default port: 8891)
*   **Requirements**: NVIDIA GPU (4GB+ VRAM), CUDA 11.8+, vLLM 0.8.5+

## Architecture & Infrastructure

*   **Database**: MySQL 8.0+ for relational data (users, workspaces, knowledge bases, documents, conversations)
*   **Vector Store**: Milvus 2.6+ for embedding storage and retrieval (30min auto-release collections)
*   **Object Storage**: MinIO 8.x for storing raw document files (PDF, TXT, Markdown, etc.)
*   **Message Queue**: RabbitMQ 3.x for asynchronous tasks (document processing, session name generation)
*   **Cache**: Redis 6.x/7.x for session, token management, and JWT blacklist
*   **Communication**:
    *   `rag-client` → `rag-server` via HTTP (REST API with JWT Bearer Auth)
    *   `rag-server` → `rag-llm` for chat/RAG requests
    *   `rag-llm` → Milvus, MinIO, RabbitMQ for document processing
    *   Optional: `rag-llm` → `embedding_rerank` services for local vectorization/reranking

## Key Conventions

### Frontend (Vue 3)
*   **Framework**: Vue 3.5.24 with Composition API
*   **Build Tool**: Vite 7.2.5 (rolldown-vite)
*   **UI Framework**: Ant Design Vue 4.2.6 + Ant Design X Vue 1.5.0
*   **Router**: Vue Router 4.6.4 (Hash mode) with `beforeEach` auth guard
*   **State Management**: Pinia 3.0.4 with localStorage persistence
    *   Core stores: `user.js` (auth), `theme.js`, `search.js`
*   **HTTP Client**: Axios 1.13.2 with Bearer Token interceptor
*   **API Base URL**: `https://www.forwardforever.top:5616/api` (configured in `consts.js`)
*   **Markdown Rendering**: markdown-it with highlight.js, MathJax3, task lists, emoji
*   **Real-time Chat**: FetchEventSource for SSE streaming responses
*   **Project Structure**:
    ```
    src/
    ├── api/               # API modules (chatApi, kbApi, workspaceApi, etc.)
    ├── stores/            # Pinia stores
    ├── router/            # Vue Router config
    ├── views/             # Page components (Dashboard, Login, chat/, kb/, workspace/)
    ├── components/        # Reusable components
    ├── layouts/           # MainLayout.vue
    ├── utils/             # Utility functions
    └── consts.js          # Constants
    ```

### Backend (Spring Boot + Java 11)
*   **Framework**: Spring Boot 2.7.6
*   **Java Version**: Java 11 (REQUIRED)
*   **ORM**: MyBatis Plus 3.5.15 with pagination interceptor
*   **Database Connection**: Druid 1.2.27
*   **Authentication**: JWT (JJWT 0.11.5, HS256 algorithm, 24h expiration)
    *   Token format: Bearer Token in Authorization header
    *   Interceptor: `JwtInterceptor` (excludes `/users/*`)
*   **Cache**: Redis (Lettuce driver, max-active: 20)
*   **Message Queue**: RabbitMQ with DirectExchange, 3 retries, Jackson2JsonMessageConverter
*   **File Storage**: MinIO 8.6.0 (S3-compatible)
*   **Vector DB**: Milvus 2.6.11
*   **Mail**: Spring Boot Mail (163 SMTP with SSL)
*   **CORS**: Global config allowing all origins, methods, headers
*   **Mapper Locations**: 
    *   Interfaces: `src/main/java/com/rag/ragserver/mapper/`
    *   XML files: `src/main/resources/com/rag/ragserver/mapper/`
    *   ⚠️ **CRITICAL**: Always update BOTH interface and XML when modifying database queries
*   **Project Structure**:
    ```
    com.rag.ragserver/
    ├── controller/        # 9 REST controllers (User, Workspace, Kb, Chat, etc.)
    ├── service/           # Business logic (interfaces + impl/)
    ├── mapper/            # MyBatis mapper interfaces (15 mappers)
    ├── domain/            # Entity classes + VO packages
    ├── dto/               # Request/Response DTOs
    ├── configuration/     # Spring config classes
    ├── interceptor/       # JWT interceptor
    ├── rabbit/            # RabbitMQ consumers
    ├── exception/         # Global exception handler
    ├── aspect/            # AOP aspects (audit logging)
    └── utils/             # Utility classes
    ```
*   **Configuration Files**:
    ```
    application.yml        # Main config (profile, port 8080, context-path: /api)
    application-dev.yml    # Development config (detailed settings)
    application-prod.yml   # Production config (template)
    ```
*   **Key Configuration**:
    *   `server.port`: 8080
    *   `server.servlet.context-path`: `/api`
    *   `jwt.secret`: Environment variable (minimum 32 characters)
    *   `jwt.expiration`: 86400000ms (24 hours)

### LLM Service (Python + FastAPI)
*   **Framework**: FastAPI with async/await
*   **Default Port**: 8888 (configured in `main.py` with `root_path="/rag"`)
*   **Core Libraries**: 
    *   LangChain (langchain, langchain_core, langchain_community, langchain_text_splitters)
    *   LangGraph (workflow orchestration)
    *   langchain_milvus (vector store integration)
*   **Async Clients**:
    *   aio_pika (RabbitMQ)
    *   miniopy_async (MinIO)
*   **Document Processing**: RecursiveCharacterTextSplitter, PyMuPDFLoader, Tesseract OCR
*   **Supported LLMs** (via `model_config.json`):
    *   OpenAI (GPT-5.2, GPT-5.2-Codex)
    *   Anthropic (Claude-4.5-Sonnet, Claude-4.5-Opus)
    *   Qwen (qwen3-max, qwen3-vl-plus, text-embedding-v4)
    *   Gemini (gemini-3-flash-preview, gemini-3-pro-preview)
    *   DeepSeek (deepseek-chat, deepseek-reasoner)
    *   Others: Moonshot, X-AI, Minimax, Xiaomi, ByteDance
*   **RabbitMQ Queues**:
    *   `session.name.generate.producer.queue` (session naming)
    *   `rag.document.process.queue` (document vectorization)
*   **Milvus Integration**: 
    *   MilvusClientManager with lifecycle management
    *   Auto-release collections after 30min inactivity
    *   Async lock for concurrent queries
*   **Configuration**: ⚠️ Hardcoded credentials in `main.py` (RABBITMQ_HOST, MINIO_ENDPOINT, MILVUS_URI, MILVUS_TOKEN). Consider using environment variables in production.
*   **Project Structure**:
    ```
    rag-llm/
    ├── main.py                      # FastAPI app entry
    ├── model_config.json            # LLM model configurations
    ├── dependencies.py              # Lifespan management
    ├── services/chat.py             # Chat routes (/chat)
    ├── mq/                          # RabbitMQ consumers
    │   ├── connection.py
    │   ├── document_embedding.py
    │   └── session_name.py
    ├── milvus_utils.py              # Milvus operations
    ├── minio_utils.py               # MinIO file storage
    ├── rag_utils.py                 # RAG core logic
    └── utils.py                     # LLM initialization
    ```

### Embedding & Rerank Services (Optional Local Services)
*   **Purpose**: Local vectorization and document reranking (eliminates external API dependency)
*   **Framework**: FastAPI + vLLM 0.8.5+ + PyTorch
*   **Models**:
    *   Embedding: Qwen/Qwen3-Embedding-0.6B (1024-dim vectors, port 8890)
    *   Rerank: Qwen/Qwen3-Reranker-0.6B (relevance scoring, port 8891)
*   **Hardware Requirements**:
    *   GPU: NVIDIA GPU with 4GB+ VRAM (recommended: 8GB+)
    *   CUDA: 11.8+
    *   Memory: 8GB+ RAM (recommended: 16GB+)
*   **Performance**:
    *   Embedding: ~100-300 texts/sec (single GPU, batch_size=32)
    *   Rerank: ~300-1000 pairs/sec (A100), ~300-600 pairs/sec (V100)
*   **Configuration**:
    *   `gpu_memory_utilization`: 0.4 (40% GPU memory)
    *   `max_model_len`: 3072 (embedding), 10000 (rerank)
    *   `max_batch_size`: 32
*   **API Endpoints**:
    *   Embedding: `/v1/embeddings`, `/embeddings`, `/health`
    *   Rerank: `/v1/rerank`, `/rerank`, `/health`
*   **Project Structure**:
    ```
    embedding_rerank/
    ├── config/                      # Configuration classes
    │   ├── embedding_config.py
    │   └── rerank_config.py
    ├── service/                     # Service implementations
    │   ├── embedding_service.py
    │   └── rerank_service.py
    ├── test/                        # Test suites
    ├── embedding_start.py           # Embedding service entry
    ├── rerank_start.py              # Rerank service entry
    └── README files                 # Detailed documentation
    ```

## Development Notes
*   **Tests**: No active test suites in `rag-client`, `rag-server`, `rag-llm`. Manual verification required. `embedding_rerank` has test files in `test/` directory.
*   **Database Schema**: Refer to `1_general_rag.sql` in root directory (15+ tables including users, workspaces, knowledgebases, documents, conversations, audit_logs)
*   **Security**: Configuration files with credentials (*.yml, model_config.json) are excluded by `.gitignore`. Use environment variables or `.example` templates.
*   **Multi-tenant**: Workspace-based isolation with fine-grained permissions (WorkspaceMembers, KbPermissions, ModelPermissions)
*   **Soft Delete**: Entities use `is_deleted` flag instead of hard deletion
*   **Audit Logging**: AOP-based audit logging via `AuditLogAspect`
