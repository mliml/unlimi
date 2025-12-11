# AI 心理咨询前端

基于 Vue 3 + Vite + Tailwind CSS + Pinia + Vue Router 构建的心理咨询平台前端。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Tailwind CSS** - 实用优先的 CSS 框架
- **Pinia** - Vue 官方状态管理库
- **Vue Router** - Vue 官方路由管理器
- **Axios** - HTTP 客户端

## 项目结构

```
frontend/
├── index.html                 # HTML 入口文件
├── package.json              # 项目依赖配置
├── vite.config.js            # Vite 配置
├── tailwind.config.js        # Tailwind CSS 配置
├── postcss.config.js         # PostCSS 配置
├── src/
│   ├── main.js               # 应用入口
│   ├── App.vue               # 根组件
│   ├── assets/
│   │   └── main.css          # 全局样式（含 Tailwind）
│   ├── router/
│   │   └── index.js          # 路由配置
│   ├── store/
│   │   └── auth.js           # 认证状态管理
│   ├── api/
│   │   ├── axios.js          # Axios 实例配置
│   │   ├── auth.js           # 认证 API
│   │   └── sessions.js       # 会话 & 问卷 API
│   ├── pages/
│   │   ├── LoginPage.vue           # 登录页
│   │   ├── RegisterPage.vue        # 注册页
│   │   ├── OnboardingPage.vue      # 初始问卷
│   │   ├── OverviewPage.vue        # 总览页
│   │   ├── ConsultPage.vue         # 咨询页
│   │   ├── HistoryPage.vue         # 历史记录页
│   │   ├── InsightsPage.vue        # 整体回顾页
│   │   ├── SettingsPage.vue        # 设置页
│   │   └── AdminPage.vue           # 管理后台
│   └── components/
│       ├── SessionList.vue         # 会话列表组件
│       ├── MessageList.vue         # 消息列表组件
│       └── ChatInput.vue           # 聊天输入组件
└── README.md
```

## 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

开发服务器将在 `http://localhost:3000` 启动。

### 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist` 目录。

### 预览生产构建

```bash
npm run preview
```

## 路由说明

### 认证路由

- `/auth/login` - 登录页
- `/auth/register` - 注册页

### 问卷路由

- `/onboarding` - 初始问卷（3 步）

### 应用路由（需要登录）

- `/app/overview` - 总览页（默认首页）
- `/app/consult` - 咨询页
- `/app/history` - 历史记录页
- `/app/insights` - 整体回顾页
- `/app/settings` - 设置页
- `/app/admin` - 管理后台

### 路由守卫

1. 未登录用户访问 `/app/*` 路由 → 重定向至 `/auth/login`
2. 已登录但未完成问卷 → 重定向至 `/onboarding`
3. 已登录且完成问卷 → 正常访问
4. 已登录用户访问 `/auth/*` 路由 → 重定向至 `/app/overview` 或 `/onboarding`

## API 配置

后端 API 地址配置在 `src/api/axios.js`：

```javascript
baseURL: 'http://127.0.0.1:8000'
```

Vite 开发服务器已配置代理，`/api` 请求会自动转发到后端。

## 状态管理

使用 Pinia 管理全局状态，当前包含：

- `auth` - 认证状态（token、用户信息、问卷完成状态）

## 本地存储

- `token` - 用户认证令牌
- `onboarding_completed` - 问卷完成标记

## API 端点

### 认证

- `POST /api/auth/login` - 登录
- `POST /api/auth/register` - 注册

### 用户

- `GET /api/me/overview` - 获取用户总览

### 会话

- `POST /api/sessions/start` - 开始咨询
- `GET /api/sessions` - 获取会话列表
- `GET /api/sessions/{id}` - 获取会话详情
- `GET /api/sessions/{id}/messages` - 获取会话消息
- `POST /api/sessions/{id}/message` - 发送消息
- `POST /api/sessions/{id}/end` - 结束会话

### 问卷

- `GET /api/onboarding/questions` - 获取问卷问题
- `POST /api/onboarding/submit` - 提交问卷答案

## 开发说明

### 代码风格

- 使用 Vue 3 Composition API（`<script setup>`）
- 使用 Tailwind CSS 进行样式开发
- 组件文件使用 PascalCase 命名
- API 调用统一封装在 `src/api/` 目录

### 扩展开发

1. 添加新页面：在 `src/pages/` 创建组件并在 `src/router/index.js` 配置路由
2. 添加新 API：在 `src/api/` 创建或扩展对应模块
3. 添加新状态：在 `src/store/` 创建新的 Pinia store

## 注意事项

1. 所有需要认证的请求会自动携带 `Authorization: Bearer {token}` 头
2. 遇到 401 响应会自动清除登录状态并跳转到登录页
3. 问卷完成状态存储在本地，清除浏览器数据会重置
