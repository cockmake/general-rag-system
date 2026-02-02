# 📢 General RAG System - 项目公告

## 🎉 核心特性

### 1. 🤖 多模型支持！深度集成主流 LLM
支持 **OpenAI GPT**、**DeepSeek**、**通义千问（Qwen）**、**Gemini** 等多种大语言模型！
- 一键切换模型，灵活选择
- 推荐使用 **通义千问系列**（Qwen-Max、Qwen-Plus）- 响应快速、质量稳定
- **DeepSeek** 性价比之选，**GPT-4** 高质量输出
- 流式响应，实时输出，体验极佳

### 2. 📚 智能 RAG 问答系统
基于检索增强生成（RAG）技术，让 AI 真正理解你的文档！
- 上传文档自动向量化（PDF、TXT、Markdown）
- 智能语义检索，精准定位相关内容
- 结合大模型生成，回答准确可靠
- 支持引用来源，可追溯可验证

### 3. 🏢 多租户 + 工作空间管理
企业级多租户架构，适合团队协作
- 工作空间隔离，数据安全可控
- 成员权限管理，灵活配置
- 多知识库支持，分类管理文档
- 完整的审计日志，操作可追溯

### 4. 💬 对话管理 + 上下文记忆
智能对话，越聊越懂你
- 多轮对话上下文管理
- 会话历史持久化
- 支持对话重命名、删除
- Markdown 渲染、代码高亮、数学公式

### 5. 🔒 隐私优先 + 本地部署
支持完全本地化部署，数据 100% 自主可控
- 可选本地向量化服务（embedding_rerank + vLLM）
- 私有知识库，敏感数据不出内网
- 支持自建 Milvus、MinIO、MySQL
- Docker 一键部署，简单快捷

### 6. 🎨 现代化 UI + 极致体验
- Vue 3 + Ant Design Vue 4 精美界面
- 深色/浅色主题随心切换
- 响应式设计，桌面移动完美适配
- 流式输出动画，打字机效果

## 🚀 技术亮点

### 前后端分离架构
- **前端**: Vue 3 + Vite + Pinia
- **后端**: Spring Boot + MyBatis Plus + JWT
- **AI 服务**: FastAPI + LangChain + LangGraph
- **向量数据库**: Milvus 2.6+
- **对象存储**: MinIO
- **消息队列**: RabbitMQ

### 高性能向量检索
- Milvus 向量数据库，毫秒级检索
- 支持多路召回策略
- 可选重排序（Rerank）优化结果
- Top-K 相似度搜索

### 异步任务处理
- RabbitMQ 消息队列
- 文档向量化异步处理
- 支持大文件、长文本

## 💡 使用建议

1. **模型选择**
   - 日常使用：推荐 **通义千问 Qwen-Plus** - 快速、稳定、性价比高
   - 高质量要求：选择 **GPT-4** 或 **Qwen-Max**
   - 成本优化：使用 **DeepSeek-Chat** 或本地模型

2. **文档管理**
   - 按主题建立不同知识库
   - 定期更新文档保持知识新鲜
   - 合理设置文档分块大小（建议 500-1000 字符）

3. **隐私安全**
   - 敏感文档建议使用本地向量化
   - 定期备份数据库和对象存储
   - 生产环境修改所有默认密码

4. **性能优化**
   - 使用 Redis 缓存提升响应速度
   - 合理配置 Milvus 索引参数
   - 启用多进程部署提高并发能力

## 🎁 完全开源免费

- ✅ 100% 开源，MIT/Apache 2.0 双协议
- ✅ 无限使用，无任何功能限制
- ✅ 支持商业使用
- ✅ 活跃开发，持续更新

## 🌟 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/cockmake/general-rag-system.git
cd general-rag-system/code

# 2. 启动依赖服务（Docker）
docker-compose up -d

# 3. 初始化数据库
mysql -u root -p general_rag < 1_general_rag.sql

# 4. 配置并启动服务
# 前端
cd rag-client && npm install && npm run dev

# 后端
cd rag-server && mvn spring-boot:run

# LLM 服务
cd rag-llm && pip install -r requirements.txt && uvicorn main:app --port 8888
```

## 📚 更多信息

- 📖 [完整文档](https://github.com/cockmake/general-rag-system)
- 🐛 [问题反馈](https://github.com/cockmake/general-rag-system/issues)
- 💬 [讨论交流](https://github.com/cockmake/general-rag-system/discussions)
- ⭐ [给个 Star](https://github.com/cockmake/general-rag-system)

## 📝 更新日志

### 最近更新（2026-02-03）
- ✨ 全面更新项目文档，与代码完全同步
- 📚 新增 embedding_rerank 本地向量化模块
- 🔧 修正 LLM 服务端口配置
- 🔒 增强安全配置说明
- 📦 更新所有依赖版本号
- 🐳 完善 Docker 部署方案

---

## ⚠️ 重要提示

1. 如遇回复错误，请刷新页面或重试
2. 首次使用需配置 API Keys（参考 SECURITY.md）
3. 生产环境请修改所有默认密码
4. 定期关注项目更新，获取新功能

## 🙏 致谢

感谢所有贡献者和使用者的支持！

如果这个项目对您有帮助，请给一个 ⭐ Star！

---

<div align="center">

**开源地址**: [https://github.com/cockmake/general-rag-system](https://github.com/cockmake/general-rag-system)

Made with ❤️ by General RAG System Contributors

</div>
