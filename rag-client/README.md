# RAG Client - 前端项目

基于 Vue 3 + Vite + Ant Design Vue 构建的现代化 RAG 系统前端界面。

## 技术栈

- **Vue 3.5+** - 渐进式 JavaScript 框架（Composition API）
- **Vite 7.x** - 下一代前端构建工具（使用 rolldown-vite）
- **Ant Design Vue 4.2+** - 企业级 UI 组件库
- **Ant Design X Vue** - AI 增强组件库
- **Pinia 3.x** - Vue 官方状态管理库
- **Vue Router 4.x** - 官方路由管理器
- **Axios 1.13+** - HTTP 请求库
- **Markdown-it** - Markdown 渲染引擎
- **Highlight.js** - 代码语法高亮
- **MathJax3** - 数学公式渲染
- **Day.js** - 轻量级时间处理库

## 功能特性

- 📝 **智能对话** - 基于 RAG 的问答交互，支持流式响应
- 📚 **文档管理** - 支持上传、查看、删除多种格式文档
- 👥 **工作空间** - 多租户隔离，成员权限管理
- 🗂️ **知识库** - 灵活的知识库组织和管理
- 🎨 **Markdown 渲染** - 支持代码高亮、数学公式、任务列表、Emoji
- 🌓 **主题切换** - 深色/浅色模式
- 📱 **响应式设计** - 适配桌面和移动端
- 🔐 **安全认证** - JWT Token 认证，Session 管理

## 快速开始

### 前置要求

- Node.js 18+ 
- npm 或 pnpm

### 安装依赖

```bash
npm install
# 或使用 pnpm（更快）
pnpm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 构建生产版本

```bash
npm run build
```

构建产物在 `dist` 目录

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
rag-client/
├── src/
│   ├── api/               # API 接口封装
│   │   ├── request.js     # Axios 实例配置
│   │   └── ...            # 各模块 API
│   ├── components/        # 公共组件
│   │   ├── ChatMessage.vue
│   │   ├── DocumentList.vue
│   │   └── ...
│   ├── views/             # 页面视图
│   │   ├── Login.vue
│   │   ├── Chat.vue
│   │   ├── Workspace.vue
│   │   └── ...
│   ├── layouts/           # 布局组件
│   │   └── MainLayout.vue
│   ├── router/            # 路由配置
│   │   └── index.js
│   ├── stores/            # Pinia 状态管理
│   │   ├── user.js
│   │   ├── workspace.js
│   │   └── ...
│   ├── utils/             # 工具函数
│   │   ├── auth.js        # 认证工具
│   │   ├── markdown.js    # Markdown 处理
│   │   └── ...
│   ├── assets/            # 静态资源
│   ├── consts.js          # 常量定义
│   ├── events.js          # 事件总线（mitt）
│   ├── vars.js            # 全局变量
│   ├── style.css          # 全局样式
│   ├── App.vue            # 根组件
│   └── main.js            # 应用入口
├── public/                # 公共静态文件
├── index.html             # HTML 入口
├── vite.config.js         # Vite 配置
├── package.json           # 项目依赖
└── README.md              # 项目文档
```

## 环境配置

创建 `.env.local` 文件配置后端地址：

```env
# 后端 API 地址
VITE_API_BASE_URL=http://localhost:8080

# LLM 服务地址（如需直连）
VITE_LLM_API_BASE_URL=http://localhost:8888

# 其他配置
VITE_APP_TITLE=General RAG System
```

### 环境变量说明

- `VITE_API_BASE_URL` - 后端 API 基础 URL（rag-server）
- `VITE_LLM_API_BASE_URL` - LLM 服务 URL（可选，通常通过 rag-server 转发）
- `VITE_APP_TITLE` - 应用标题

## 部署

### 静态部署

将 `dist` 目录部署到 Nginx、Apache 或云存储（OSS/S3）。

#### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # 前端静态资源
    location / {
        root /var/www/rag-client/dist;
        try_files $uri $uri/ /index.html;
        
        # 缓存策略
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # 后端 API 代理
    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如有流式响应）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Docker 部署

```dockerfile
# Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

构建和运行：

```bash
docker build -t rag-client:1.0.0 .
docker run -d -p 80:80 rag-client:1.0.0
```

## 开发指南

### 代码规范

- 使用 ESLint 进行代码检查
- 遵循 Vue 3 Composition API 风格指南
- 组件命名使用 PascalCase
- 文件命名使用 kebab-case

### 调试技巧

1. **Vue DevTools** - 安装 Vue 浏览器扩展
2. **网络请求** - 使用浏览器开发者工具 Network 面板
3. **状态管理** - Pinia DevTools 查看状态变化
4. **日志输出** - 控制台查看 `console.log` 输出

### 常见问题

**Q: Vite 启动失败？**
A: 检查 Node.js 版本是否 >= 18，清除 node_modules 后重新安装。

**Q: API 请求跨域？**
A: 在 `vite.config.js` 中配置代理或在后端启用 CORS。

**Q: Markdown 渲染异常？**
A: 检查 markdown-it 及其插件版本是否兼容。

## 相关文档

- [Vue 3 官方文档](https://vuejs.org/)
- [Vite 官方文档](https://vitejs.dev/)
- [Ant Design Vue 文档](https://antdv.com/)
- [Pinia 官方文档](https://pinia.vuejs.org/)

## 返回主文档

查看完整系统文档：[../README.md](../README.md)
