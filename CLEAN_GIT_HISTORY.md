# 清理Git历史中的敏感信息

## 背景

文件 `rag-llm/advanced_rag_example.py` 包含泄露的API密钥，已在最新提交中删除。但该文件仍存在于Git历史记录中。

## 泄露的API密钥

⚠️ **以下密钥必须立即撤销/重新生成：**

1. **阿里云通义千问 API Key**: `sk-188e60cd3e844cab97bc30138dac5cd7`
2. **DeepSeek API Key**: `sk-e34cc6e3056045bea1da92160035e0df`

## 立即行动清单

### 1. 撤销泄露的API密钥（最高优先级）

- [ ] 登录阿里云控制台，撤销通义千问API Key: `sk-188e60cd3e844cab97bc30138dac5cd7`
- [ ] 登录DeepSeek平台，撤销API Key: `sk-e34cc6e3056045bea1da92160035e0df`
- [ ] 生成新的API密钥并更新到 `model_config.json`（不要提交到Git）
- [ ] 检查两个平台的API调用日志，确认是否有异常使用

### 2. 清理Git历史记录

由于文件已被提交到Git历史，需要彻底清理：

#### 方法一：使用 git filter-repo（推荐）

```bash
# 1. 安装 git-filter-repo
pip install git-filter-repo

# 2. 创建仓库备份
cd ..
cp -r code code-backup

# 3. 清理历史记录
cd code
git filter-repo --path rag-llm/advanced_rag_example.py --invert-paths

# 4. 强制推送到远程仓库（如果已推送）
git push origin --force --all
git push origin --force --tags
```

#### 方法二：使用 BFG Repo-Cleaner

```bash
# 1. 下载 BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/

# 2. 运行清理
java -jar bfg.jar --delete-files advanced_rag_example.py code.git

# 3. 清理引用和垃圾回收
cd code
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. 强制推送
git push origin --force --all
```

#### 方法三：使用 git filter-branch（较慢但内置）

```bash
cd code

# 从所有历史记录中删除文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch rag-llm/advanced_rag_example.py" \
  --prune-empty --tag-name-filter cat -- --all

# 清理引用
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 强制推送
git push origin --force --all
git push origin --force --tags
```

### 3. 通知协作者

如果有其他开发者已经克隆了仓库：

1. **通知所有协作者**不要再推送基于旧历史的更改
2. 要求他们：
   ```bash
   # 删除本地仓库
   cd ..
   rm -rf code
   
   # 重新克隆清理后的仓库
   git clone <repository-url>
   cd code
   ```

### 4. 验证清理结果

```bash
# 搜索Git历史中是否还有泄露的密钥
git log --all --full-history --source --oneline -- rag-llm/advanced_rag_example.py

# 搜索是否还包含密钥字符串
git grep "sk-188e60cd3e844cab97bc30138dac5cd7" $(git rev-list --all)
git grep "sk-e34cc6e3056045bea1da92160035e0df" $(git rev-list --all)

# 如果没有输出，说明已清理干净
```

### 5. 预防措施

#### 已完成
- [x] 已更新 `.gitignore` 排除敏感配置文件
- [x] 已创建 `.example` 模板文件
- [x] 已添加 SECURITY.md 安全配置指南
- [x] 已更新所有 README 文档说明配置方式

#### 建议实施
- [ ] 设置 pre-commit hook 扫描敏感信息
- [ ] 使用环境变量或密钥管理服务（如 Vault）
- [ ] 启用 GitHub Secret Scanning（如果使用 GitHub）
- [ ] 定期审计代码库中的敏感信息
- [ ] 团队培训：不要硬编码敏感信息

#### ⚠️ 特别注意

`rag-llm/main.py` 中仍包含硬编码的基础设施连接信息：

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

**生产环境部署前务必修改！** 建议：
1. 改为从环境变量读取
2. 使用配置文件（已在 .gitignore 中）
3. 使用配置管理工具

## Pre-commit Hook 示例

创建 `.git/hooks/pre-commit` 文件：

```bash
#!/bin/bash

# 检查是否包含API密钥模式
if git diff --cached | grep -E "api_key\s*=\s*['\"]sk-[a-zA-Z0-9]{32,}"; then
    echo "错误：检测到硬编码的API密钥！"
    echo "请使用环境变量或配置文件（已在.gitignore中）存储密钥。"
    exit 1
fi

# 检查敏感文件
SENSITIVE_FILES="model_config.json application-dev.yml application-prod.yml"
for file in $SENSITIVE_FILES; do
    if git diff --cached --name-only | grep -q "$file"; then
        echo "警告：正在提交敏感配置文件 $file"
        echo "请确认该文件不包含真实密钥，或已在.gitignore中。"
        exit 1
    fi
done

exit 0
```

使其可执行：
```bash
chmod +x .git/hooks/pre-commit
```

## 参考资源

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [git-filter-repo 文档](https://github.com/newren/git-filter-repo)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)

## 时间线

- **2026-01-13**: 发现泄露，删除文件，更新 .gitignore 和 SECURITY.md
- **2026-02-02**: 全面更新项目文档，添加配置安全说明
  - 更新根目录 README.md
  - 更新所有子项目 README（rag-client、rag-server、rag-llm）
  - 新增 embedding_rerank/README.md
  - 更新 SECURITY.md（增加 main.py 配置警告）
  - 更新 CONTRIBUTING.md（增加开发规范）
  - 更新 CLEAN_GIT_HISTORY.md（本文件）
- **待执行**: 撤销泄露的 API 密钥
- **待执行**: 清理 Git 历史（可选，如需彻底清除）
- **待执行**: 重构 `rag-llm/main.py` 配置方式

## 后续改进计划

1. **配置管理优化**
   - 将 `main.py` 中的硬编码配置改为环境变量
   - 创建统一的配置加载模块
   - 支持多环境配置切换（dev/test/prod）

2. **安全加固**
   - 实施 pre-commit hooks
   - 集成 Secret Scanning 工具
   - 添加配置文件加密方案

3. **文档维护**
   - 定期更新版本号和依赖版本
   - 保持所有 README 与实际代码同步
   - 添加更多使用示例和最佳实践
