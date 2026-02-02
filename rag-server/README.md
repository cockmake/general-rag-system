# RAG Server - 后端服务

基于 Spring Boot 的 RAG 系统后端服务，提供用户管理、工作空间管理、文档管理、知识库管理和向量检索等核心功能。

## 技术栈

- **Spring Boot 2.7.6** - 企业级 Java 应用框架
- **Java 11** - JDK 版本（必须使用 Java 11）
- **Maven 3.6+** - 项目构建工具
- **MyBatis Plus 3.x** - 增强的持久层框架
- **MySQL 8.0+** - 关系型数据库
- **Redis 6.x/7.x** - 缓存和 Session 存储
- **Milvus SDK 2.6.11** - 向量数据库 Java 客户端
- **MinIO SDK 8.6.0** - 对象存储 Java 客户端
- **JWT (jjwt 0.11.5)** - Token 认证
- **RabbitMQ** - 消息队列（异步任务）

## 功能模块

- 🔐 **用户认证与授权** - JWT Token、Session 管理、权限控制
- 👥 **工作空间管理** - 多租户隔离、成员管理、角色权限
- 📚 **知识库管理** - 创建、配置、共享知识库
- 📄 **文档管理** - 上传、解析、向量化、版本控制
- 💬 **对话管理** - 会话持久化、历史记录、上下文管理
- 🔍 **向量检索** - Milvus 集成、相似度搜索
- 📊 **审计日志** - 操作记录、行为追踪
- 🔗 **LLM 服务集成** - 与 rag-llm 服务通信

## 快速开始

### 前置要求

- **JDK 11**（必须，不支持其他版本）
- Maven 3.6+
- MySQL 8.0+
- Redis 6.x 或 7.x
- Milvus 2.6+
- MinIO
- RabbitMQ 3.x

### 数据库初始化

```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE general_rag DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 导入表结构（在项目根目录）
mysql -u root -p general_rag < ../1_general_rag.sql
```

### 配置文件

⚠️ **重要**：敏感配置文件已在 `.gitignore` 中排除，需手动创建。

#### 1. 复制配置模板

```bash
cd src/main/resources

# 开发环境配置
cp application-dev.yml.example application-dev.yml

# 生产环境配置
cp application-prod.yml.example application-prod.yml
```

#### 2. 修改配置文件

编辑 `application-dev.yml` 或 `application-prod.yml`：

```yaml
spring:
  application:
    name: rag-server
  datasource:
    url: jdbc:mysql://localhost:3306/general_rag?useUnicode=true&characterEncoding=utf8mb4&serverTimezone=Asia/Shanghai
    username: root
    password: your_mysql_password  # 修改为真实密码
  redis:
    host: localhost
    port: 6379
    password: your_redis_password  # 修改为真实密码
  rabbitmq:
    host: localhost
    port: 5672
    username: admin
    password: your_rabbitmq_password  # 修改为真实密码

server:
  port: 8080

# Milvus 配置
milvus:
  uri: http://localhost:19530
  token: username:password  # 修改为真实认证信息

# MinIO 配置
minio:
  endpoint: http://localhost:9000
  access-key: your_access_key  # 修改为真实 Access Key
  secret-key: your_secret_key  # 修改为真实 Secret Key
  bucket-name: rag-documents

# JWT 配置
jwt:
  secret: your-jwt-secret-key-at-least-32-characters  # 生成强密钥
  expiration: 86400000  # 24小时（毫秒）

# LLM 服务配置
llm:
  service:
    url: http://localhost:8888  # rag-llm 服务地址
```

#### 3. 生成 JWT 密钥

```bash
# 使用 OpenSSL
openssl rand -base64 32

# 或使用 Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 构建运行

```bash
# 安装依赖并编译
mvn clean install

# 启动开发服务器
mvn spring-boot:run

# 指定配置文件启动
mvn spring-boot:run -Dspring-boot.run.profiles=dev

# 或打包后运行
mvn clean package
java -jar target/rag-server-1.0.0.jar

# 生产环境运行
java -jar target/rag-server-1.0.0.jar --spring.profiles.active=prod
```

服务将在 `http://localhost:8080` 启动。

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8080/actuator/health

# 检查数据库连接
curl http://localhost:8080/actuator/health/db
```

## API 文档

### 主要接口

#### 认证相关
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/logout` - 退出登录
- `GET /api/auth/me` - 获取当前用户信息

#### 工作空间
- `GET /api/workspaces` - 工作空间列表
- `POST /api/workspaces` - 创建工作空间
- `PUT /api/workspaces/{id}` - 更新工作空间
- `DELETE /api/workspaces/{id}` - 删除工作空间

#### 知识库
- `GET /api/knowledgebases` - 知识库列表
- `POST /api/knowledgebases` - 创建知识库
- `GET /api/knowledgebases/{id}` - 知识库详情
- `DELETE /api/knowledgebases/{id}` - 删除知识库

#### 文档管理
- `POST /api/documents/upload` - 上传文档
- `GET /api/documents` - 文档列表
- `GET /api/documents/{id}` - 文档详情
- `DELETE /api/documents/{id}` - 删除文档

#### 对话管理
- `POST /api/conversations` - 创建会话
- `GET /api/conversations` - 会话列表
- `POST /api/conversations/{id}/messages` - 发送消息
- `GET /api/conversations/{id}/messages` - 消息历史

#### 向量检索
- `POST /api/search` - 向量相似度搜索
- `POST /api/rag/query` - RAG 问答（流式）

### 认证方式

所有需要认证的接口，请在请求头中携带 Token：

```bash
Authorization: Bearer <your_jwt_token>
```

### 接口调用示例

```bash
# 登录获取 Token
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# 使用 Token 访问受保护接口
curl -X GET http://localhost:8080/api/workspaces \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 上传文档
curl -X POST http://localhost:8080/api/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "knowledgebaseId=1"
```

## 部署

### Docker 部署

#### 1. 创建 Dockerfile

```dockerfile
FROM openjdk:11-jre-slim

WORKDIR /app

# 复制 JAR 文件
COPY target/rag-server-1.0.0.jar app.jar

# 暴露端口
EXPOSE 8080

# JVM 参数优化
ENV JAVA_OPTS="-Xms512m -Xmx2048m -XX:+UseG1GC -XX:MaxGCPauseMillis=200"

# 启动应用
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

#### 2. 构建和运行

```bash
# 构建镜像
docker build -t rag-server:1.0.0 .

# 运行容器
docker run -d -p 8080:8080 \
  -e SPRING_PROFILES_ACTIVE=prod \
  -e MYSQL_HOST=mysql \
  -e REDIS_HOST=redis \
  -e MILVUS_URI=http://milvus:19530 \
  -e MINIO_ENDPOINT=http://minio:9000 \
  --name rag-server \
  rag-server:1.0.0
```

### 生产环境配置

#### 1. 系统要求

- 内存：最低 2GB，推荐 4GB+
- CPU：2 核心以上
- 存储：根据文档量调整

#### 2. JVM 参数调优

```bash
java -jar \
  -Xms2g \
  -Xmx4g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/var/log/rag-server/ \
  -Dspring.profiles.active=prod \
  target/rag-server-1.0.0.jar
```

#### 3. 日志配置

在 `application-prod.yml` 中配置日志：

```yaml
logging:
  level:
    root: INFO
    com.rag.ragserver: INFO
  file:
    name: /var/log/rag-server/application.log
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} - %msg%n"
    file: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
```

#### 4. 监控和健康检查

启用 Spring Boot Actuator：

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: when-authorized
```

#### 5. 反向代理（Nginx）

```nginx
upstream rag-server {
    server localhost:8080;
}

server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://rag-server;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## 开发指南

### 代码规范

- 遵循阿里巴巴 Java 开发手册
- 使用 Maven Checkstyle 插件检查
- 类名使用 PascalCase，方法名使用 camelCase
- 接口统一返回 `Result<T>` 格式

### MyBatis 使用注意事项

⚠️ **重要**：MyBatis XML 映射文件位置

- XML 文件位置：`src/main/resources/com/rag/ragserver/mapper/`
- 修改 Mapper 接口时，必须同步更新对应的 XML 文件
- 确保命名空间与 Mapper 接口全限定名一致

### 本地调试

```bash
# 开启调试模式
mvn spring-boot:run -Dspring-boot.run.jvmArguments="-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=5005"
```

在 IDE 中配置远程调试，连接端口 5005。

### 常见问题

**Q: 启动失败，提示数据库连接错误？**
A: 检查 MySQL 是否已启动，数据库是否已创建，配置文件中的用户名密码是否正确。

**Q: JWT Token 验证失败？**
A: 确保 JWT Secret 配置一致，检查 Token 是否过期。

**Q: MyBatis 映射文件找不到？**
A: 检查 XML 文件是否在 `src/main/resources/com/rag/ragserver/mapper/` 目录下。

## 相关文档

- [Spring Boot 官方文档](https://spring.io/projects/spring-boot)
- [MyBatis Plus 官方文档](https://baomidou.com/)
- [Milvus Java SDK](https://milvus.io/docs/install-java.md)

## 返回主文档

查看完整系统文档：[../README.md](../README.md)

## 项目结构

```
rag-server/
├── src/
│   ├── main/
│   │   ├── java/com/rag/ragserver/
│   │   │   ├── RagServerApplication.java     # 主启动类
│   │   │   ├── controller/                   # 控制器层
│   │   │   │   ├── AuthController.java
│   │   │   │   ├── WorkspaceController.java
│   │   │   │   ├── KnowledgebaseController.java
│   │   │   │   ├── DocumentController.java
│   │   │   │   └── ...
│   │   │   ├── service/                      # 业务逻辑层
│   │   │   │   ├── impl/                     # 实现类
│   │   │   │   └── ...
│   │   │   ├── mapper/                       # MyBatis 数据访问层
│   │   │   │   ├── UserMapper.java
│   │   │   │   └── ...
│   │   │   ├── domain/                       # 实体类
│   │   │   │   ├── User.java
│   │   │   │   ├── Workspace.java
│   │   │   │   └── ...
│   │   │   ├── dto/                          # 数据传输对象
│   │   │   │   ├── LoginDTO.java
│   │   │   │   └── ...
│   │   │   ├── configuration/                # 配置类
│   │   │   │   ├── SecurityConfig.java
│   │   │   │   ├── MilvusConfig.java
│   │   │   │   └── ...
│   │   │   ├── interceptor/                  # 拦截器
│   │   │   │   └── JwtInterceptor.java
│   │   │   ├── aspect/                       # AOP 切面
│   │   │   ├── exception/                    # 异常处理
│   │   │   ├── assembler/                    # 对象转换
│   │   │   ├── rabbit/                       # RabbitMQ 消费者
│   │   │   ├── common/                       # 公共类
│   │   │   └── utils/                        # 工具类
│   │   └── resources/
│   │       ├── application.yml               # 主配置
│   │       ├── application-dev.yml           # 开发环境（需创建）
│   │       ├── application-prod.yml          # 生产环境（需创建）
│   │       ├── application-dev.yml.example   # 开发环境模板
│   │       ├── application-prod.yml.example  # 生产环境模板
│   │       ├── com/rag/ragserver/mapper/     # MyBatis XML 映射文件
│   │       │   ├── UserMapper.xml
│   │       │   └── ...
│   │       └── logback-spring.xml            # 日志配置
│   └── test/                                 # 测试代码
├── pom.xml                                   # Maven 配置
└── README.md                                 # 本文件
```
