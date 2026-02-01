# General RAG System Copilot Instructions

## Project Structure

This repository contains a full-stack RAG (Retrieval-Augmented Generation) system composed of three main microservices:

*   **`rag-client`**: Frontend application (Vue 3 + Vite + Ant Design Vue).
*   **`rag-server`**: Backend business service (Spring Boot + MyBatis Plus). Handles authentication, document management, and business logic.
*   **`rag-llm`**: AI/ML service (Python + FastAPI + LangChain). Handles vector embedding (Milvus), LLM inference, and document processing.

## Build and Run Commands

### Frontend (`rag-client`)
*   **Install dependencies**: `npm install`
*   **Start development server**: `npm run dev`
*   **Build for production**: `npm run build`
*   **Preview build**: `npm run preview`

### Backend (`rag-server`)
*   **Start application**: `mvn spring-boot:run`
*   **Clean and install**: `mvn clean install`
*   **Configuration**:
    *   Main config: `src/main/resources/application.yml`
    *   Environment overrides: `application-dev.yml`, `application-prod.yml`

### LLM Service (`rag-llm`)
*   **Install dependencies**: `pip install -r requirements.txt`
*   **Start server**: `uvicorn main:app --host 0.0.0.0 --port 8888 --workers 2`
    *   Note: The service runs on port 8888 by default as per `main.py` comments.

## Architecture & Infrastructure

*   **Database**: MySQL for relational data (users, workspaces, metadata).
*   **Vector Store**: Milvus for embedding storage and retrieval.
*   **Object Storage**: MinIO for storing raw document files (PDF, TXT, etc.).
*   **Message Queue**: RabbitMQ for asynchronous tasks (likely document processing pipelines).
*   **Cache**: Redis for session and token management.
*   **Communication**:
    *   Frontend talks to `rag-server` via HTTP.
    *   `rag-server` likely orchestrates calls to `rag-llm` and other infrastructure.

## Key Conventions

### Backend (Java)
*   **Persistence**: Uses MyBatis Plus.
*   **Mapper Locations**: XML Mappers are located in `src/main/resources/com/rag/ragserver/mapper/`. Always update the XML file when modifying mapper interfaces.
*   **Java Version**: Java 11.

### LLM Service (Python)
*   **Configuration**: Key environment variables (RabbitMQ, MinIO, Milvus credentials) are currently set in `main.py`. Be cautious when editing this file to avoid committing sensitive hardcoded credentials.
*   **Libraries**: Uses `langchain` and `langgraph` for RAG flows.

### Frontend (Vue)
*   **UI Framework**: Ant Design Vue.
*   **State Management**: Pinia.
*   **Markdown**: Uses `markdown-it` with various plugins (highlight.js, mathjax) for rendering chat responses.

## Development Notes
*   **Tests**: There are currently no active test suites detected in the standard locations for any of the three modules. Focus on manual verification after changes.
*   **Database Schema**: Refer to `1_general_rag.sql` in the root for the database structure.
