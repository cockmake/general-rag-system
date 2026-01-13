# RAG Client - 前端项目

基于 Vue.js 3 + Vite 构建的 RAG 系统前端界面。

## 技术栈

- Vue.js 3
- Vite
- Axios（HTTP请求）

## 开发环境

### 安装依赖

```bash
npm install
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

## 项目结构

```
src/
├── components/     # 组件
├── views/         # 页面
├── router/        # 路由
├── store/         # 状态管理
├── api/           # API接口
└── utils/         # 工具函数
```

## 环境配置

创建 `.env.local` 文件配置后端地址：

```
VITE_API_BASE_URL=http://localhost:8080
```

## 部署

将 `dist` 目录部署到 Nginx 或其他静态服务器。

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend-server:8080;
    }
}
```
