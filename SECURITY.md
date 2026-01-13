# 安全配置指南

## ⚠️ 重要提醒

**请勿将包含敏感信息的配置文件提交到 Git 仓库！**

## 配置文件说明

### 后端配置 (rag-server)

1. 复制示例配置文件：
```bash
cp rag-server/src/main/resources/application-dev.yml.example rag-server/src/main/resources/application-dev.yml
cp rag-server/src/main/resources/application-prod.yml.example rag-server/src/main/resources/application-prod.yml
```

2. 修改配置文件，填入真实的：
   - 数据库密码
   - JWT 密钥（至少32位随机字符串）
   - MinIO 访问密钥
   - RabbitMQ 密码
   - Redis 密码
   - 邮箱授权码
   - Milvus 认证信息

### LLM服务配置 (rag-llm)

1. 复制示例配置文件：
```bash
cp rag-llm/model_config.json.example rag-llm/model_config.json
```

2. 填入各AI服务商的 API Key：
   - OpenAI
   - DeepSeek
   - 通义千问（Qwen）
   - Gemini
   - 其他LLM服务

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

- `rag-server/src/main/resources/application-dev.yml`
- `rag-server/src/main/resources/application-prod.yml`
- `rag-llm/model_config.json`
- 所有 `.env` 文件

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
```

## 紧急处理

如果不小心提交了敏感信息：

1. **立即更换所有泄露的密钥和密码**
2. 从 Git 历史中删除敏感文件：
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch rag-server/src/main/resources/application-dev.yml" \
  --prune-empty --tag-name-filter cat -- --all
```

3. 强制推送：
```bash
git push origin --force --all
```

4. 通知所有协作者重新克隆仓库
