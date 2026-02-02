# 安全配置指南

## 🚨 紧急通知：API密钥已泄露

**时间：2026-01-13**

文件 `rag-llm/advanced_rag_example.py` 中包含的以下API密钥已被暴露在Git历史记录中并已删除：

1. **阿里云通义千问 API Key**: `sk-188e60cd3e844cab97bc30138dac5cd7`
2. **DeepSeek API Key**: `sk-e34cc6e3056045bea1da92160035e0df`

⚠️ **必须立即采取的行动：**
- ✅ 泄露的文件已被删除
- ⚠️ **请立即前往相应平台撤销/重新生成以上API密钥**
- ⚠️ **检查API使用记录，确认是否有异常调用**
- ⚠️ Git历史中仍包含这些密钥，建议使用 BFG Repo-Cleaner 或 git filter-repo 清理历史

---

## ⚠️ 重要提醒

**请勿将包含敏感信息的配置文件提交到 Git 仓库！**

本项目的配置文件包含数据库密码、API 密钥等敏感信息，必须妥善保管。

## 受影响的配置文件

### 后端配置 (rag-server)

以下文件已在 `.gitignore` 中排除，需手动创建：

- `rag-server/src/main/resources/application-dev.yml`
- `rag-server/src/main/resources/application-prod.yml`

项目提供了对应的 `.example` 模板文件。

2. 修改配置文件，填入真实的：
   - **数据库密码** (MySQL)
   - **JWT 密钥**（至少32位随机字符串）
   - **MinIO 访问密钥** (Access Key & Secret Key)
   - **RabbitMQ 密码**
   - **Redis 密码**
   - **邮箱授权码**（如使用邮件功能）
   - **Milvus 认证信息** (Token格式: username:password)

### LLM服务配置 (rag-llm)

以下文件已在 `.gitignore` 中排除，需手动创建：

- `rag-llm/model_config.json`

⚠️ **额外注意**：`rag-llm/main.py` 中硬编码了基础设施连接信息：

```python
os.environ["RABBITMQ_HOST"] = "192.168.188.6"
os.environ["RABBITMQ_PORT"] = "5678"
os.environ["RABBITMQ_USERNAME"] = "make"
os.environ["RABBITMQ_PASSWORD"] = "make20260101"

os.environ["MINIO_ENDPOINT"] = "192.168.188.6:9002"
os.environ["MINIO_ACCESS_KEY"] = "make"
os.environ["MINIO_SECRET_KEY"] = "make20260101"

os.environ["MILVUS_URI"] = "http://192.168.188.6:19530"
os.environ["MILVUS_TOKEN"] = "make:make5211314"
```

**生产环境部署时必须修改这些配置！** 建议：
1. 使用环境变量替代硬编码
2. 创建独立的配置文件
3. 使用配置管理工具（如 Vault）

### 配置步骤

#### 1. 后端配置

```bash
cd rag-server/src/main/resources
cp application-dev.yml.example application-dev.yml
cp application-prod.yml.example application-prod.yml
# 编辑文件，填入真实配置
```

#### 2. LLM 服务配置

```bash
cd rag-llm
cp model_config.json.example model_config.json
# 编辑文件，填入真实 API Keys

# 同时修改 main.py 中的硬编码配置
```

## 环境变量方式（推荐生产环境）

### 后端服务

```bash
export MYSQL_PASSWORD=your_password
export JWT_SECRET=your_secret
export MINIO_SECRET_KEY=your_key
export REDIS_PASSWORD=your_password
```

### LLM服务

```bash
export OPENAI_API_KEY=your_key
export DEEPSEEK_API_KEY=your_key
export QWEN_API_KEY=your_key
export GEMINI_API_KEY=your_key

# 基础设施连接（替代 main.py 中的硬编码）
export RABBITMQ_HOST=localhost
export RABBITMQ_PORT=5672
export RABBITMQ_USERNAME=admin
export RABBITMQ_PASSWORD=your_password

export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=your_access_key
export MINIO_SECRET_KEY=your_secret_key

export MILVUS_URI=http://localhost:19530
export MILVUS_TOKEN=username:password
```

## 密钥生成建议

### JWT Secret
```bash
# Linux/Mac
openssl rand -base64 32

# 或使用 Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 强密码
```bash
# 生成强密码
openssl rand -base64 16
```

## 已忽略的文件

以下文件已在 `.gitignore` 中配置，不会被提交：

**后端配置：**
- `rag-server/src/main/resources/application-dev.yml`
- `rag-server/src/main/resources/application-prod.yml`

**LLM 服务配置：**
- `rag-llm/model_config.json`

**其他：**
- 所有 `.env` 文件
- 所有 `*_example.py` 文件（如包含敏感数据）

⚠️ **注意**：`rag-llm/main.py` 本身不在 `.gitignore` 中，请确保不要提交包含真实密码的版本。

## 检查清单

上传代码前，请确保：

- [ ] 所有包含密钥的配置文件已在 `.gitignore` 中
- [ ] 已创建对应的 `.example` 示例文件
- [ ] 示例文件中不包含真实密钥
- [ ] 运行 `git status` 检查是否有敏感文件未被忽略

## 验证命令

```bash
# 检查是否有敏感信息将被提交
git status

# 检查 .gitignore 是否生效
git check-ignore -v rag-server/src/main/resources/application-dev.yml
git check-ignore -v rag-llm/model_config.json

# 搜索代码中是否包含敏感关键词（不建议硬编码）
grep -r "sk-" --include="*.py" --exclude-dir=".git"
grep -r "password.*=" --include="*.yml" --exclude-dir=".git"

# 查看即将提交的内容（确保不含敏感信息）
git diff --cached
```

## 紧急处理

如果不小心提交了敏感信息：

### 1. 立即更换所有泄露的密钥和密码

**必须优先完成，否则清理历史也无用！**

- 数据库密码
- API Keys (OpenAI、DeepSeek、通义千问等)
- JWT Secret
- MinIO/Redis/RabbitMQ 凭据
- 其他所有暴露的敏感信息

### 2. 从 Git 历史中删除敏感文件

#### 方法一：使用 git filter-repo（推荐）

```bash
# 安装
pip install git-filter-repo

# 备份仓库
cp -r . ../backup

# 删除文件
git filter-repo --path rag-llm/advanced_rag_example.py --invert-paths

# 强制推送
git push origin --force --all
git push origin --force --tags
```

#### 方法二：使用 BFG Repo-Cleaner

```bash
# 下载 BFG
# https://rtyley.github.io/bfg-repo-cleaner/

# 清理
java -jar bfg.jar --delete-files sensitive_file.py

# 清理垃圾
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 强制推送
git push origin --force --all
```

### 3. 通知协作者

发送通知给所有协作者：

```
紧急通知：Git 历史已重写，请执行以下操作：

1. 备份本地未推送的更改
2. 删除本地仓库
3. 重新克隆：git clone <repo-url>
4. 应用之前的更改

请勿基于旧历史推送代码，否则会将敏感信息重新引入。
```

### 4. 检查是否已上传到公共平台

如果代码已推送到 GitHub/GitLab 等公共平台：

- GitHub 会自动扫描泄露的 API Keys
- 检查邮箱是否收到 GitHub 的安全警报
- 如果已被索引，联系平台支持永久删除

### 5. 安全审计

```bash
# 检查历史记录是否还有敏感信息
git log --all --full-history --source --oneline -- <file_path>

# 搜索特定字符串
git grep "api_key" $(git rev-list --all)
git grep "password" $(git rev-list --all)
```
