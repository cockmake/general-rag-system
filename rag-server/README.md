# RAG Server - 后端服务

基于 Spring Boot 的 RAG 系统后端服务，提供用户管理、文档管理和向量检索等功能。

## 技术栈

- Spring Boot 2.7.6
- Java 11
- Maven
- Milvus SDK（向量数据库）
- MinIO SDK（对象存储）
- JWT（身份认证）

## 功能模块

- 用户认证与授权
- 文档上传与管理
- 向量数据存储与检索
- 与 LLM 服务交互

## 快速开始

### 前置要求

- JDK 11+
- Maven 3.6+
- Milvus 2.x
- MinIO

### 配置文件

修改 `src/main/resources/application.yml`：

```yaml
spring:
  application:
    name: rag-server

server:
  port: 8080

# Milvus配置
milvus:
  host: localhost
  port: 19530

# MinIO配置
minio:
  endpoint: http://localhost:9000
  access-key: your-access-key
  secret-key: your-secret-key
  bucket-name: rag-files

# JWT配置
jwt:
  secret: your-jwt-secret-key
  expiration: 86400000
```

### 构建运行

```bash
# 编译
mvn clean package

# 运行
mvn spring-boot:run

# 或直接运行 jar
java -jar target/rag-server-1.0.0.jar
```

## API 文档

启动后访问 Swagger UI（如已配置）：
```
http://localhost:8080/swagger-ui.html
```

主要接口：
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `POST /api/documents/upload` - 上传文档
- `GET /api/documents` - 文档列表
- `POST /api/search` - 向量检索

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t rag-server:1.0.0 .

# 运行容器
docker run -d -p 8080:8080 \
  -e MILVUS_HOST=milvus \
  -e MINIO_ENDPOINT=http://minio:9000 \
  rag-server:1.0.0
```

### 生产环境配置

- 修改数据库连接配置
- 配置日志输出路径
- 设置 JVM 参数
- 配置监控和健康检查

## 开发说明

项目结构：
```
src/main/java/com/rag/
├── controller/     # 控制器
├── service/        # 业务逻辑
├── repository/     # 数据访问
├── entity/         # 实体类
├── dto/            # 数据传输对象
├── config/         # 配置类
└── util/           # 工具类
```
