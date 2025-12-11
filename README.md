<h1 align="center">Unlimi AI Therapy</h1>

<div align="center">
  🧠💬🌿
</div>
<div align="center">
  <strong>多智能体驱动的本地化心理咨询平台</strong>
</div>
<div align="center">
  100% 本地部署，连续、可信赖的 AI 心理支持
</div>

<br />

<div align="center">
  <!-- Status -->
  <a href="#">
    <img src="https://img.shields.io/badge/status-alpha-orange.svg?style=flat-square" alt="项目状态" />
  </a>
  <!-- Backend -->
  <a href="#">
    <img src="https://img.shields.io/badge/backend-FastAPI-blue.svg?style=flat-square" alt="Backend" />
  </a>
  <!-- Frontend -->
  <a href="#">
    <img src="https://img.shields.io/badge/frontend-Vue%203%20%2B%20Vite-41b883.svg?style=flat-square" alt="Frontend" />
  </a>
  <!-- Database -->
  <a href="#">
    <img src="https://img.shields.io/badge/database-PostgreSQL-336791.svg?style=flat-square" alt="Database" />
  </a>
  <!-- AI -->
  <a href="#">
    <img src="https://img.shields.io/badge/AI-GPT--4o%20%2B%20Agno-6b4eff.svg?style=flat-square" alt="AI Stack" />
  </a>
</div>

<div align="center">
  <h3>
    <a href="./PROJECT_INTRODUCTION.md">产品概览</a>
    <span> | </span>
    <a href="./docs/guide.md">使用指南</a>
    <span> | </span>
    <a href="./docs/API_PROMPTS_MANAGEMENT.md">提示词管理</a>
    <span> | </span>
    <a href="./frontend/README.md">前端说明</a>
  </h3>
</div>

<div align="center">
  <sub>由多智能体协作打造的心理健康支持工具，感谢所有贡献者的付出。</sub>
</div>

## 目录
- [功能亮点](#功能亮点)
- [示例体验](#示例体验)
- [核心理念](#核心理念)
- [多智能体架构](#多智能体架构)
- [记忆与数据](#记忆与数据)
- [前端体验](#前端体验)
- [部署与运行](#部署与运行)
- [API 速览](#api-速览)
- [性能与优化](#性能与优化)
- [FAQ](#faq)
- [路线图](#路线图)
- [贡献与支持](#贡献与支持)
- [许可证](#许可证)

## 功能亮点
- **专业咨询对话**：基于 GPT-4o 的 TherapistAgent，提供具备共情和认知行为疗法风格的实时回复。
- **自动记忆管理**：对话要点自动抽取与持久化，跨会话连续跟进，无需手动记录。
- **智能会话总结**：ClerkAgent 在会话结束生成总结、关键事件与情绪洞察，辅助复盘。
- **本地隐私优先**：全部数据落地 PostgreSQL，本地可控；JWT 鉴权与分级访问控制。
- **轻量前端**：Vue 3 + Vite + Tailwind，支持咨询、历史回顾、画像与管理面板。
- **可扩展架构**：多模型协作、工具扩展、可插拔的 Agent、可配置的运行参数。

## 示例体验
```bash
# 1) 健康检查
curl http://localhost:8000/health
# => {"status": "ok"}

# 2) 注册并获取 token
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"Passw0rd!"}'
# => 返回 access_token，用于后续授权

# 3) 创建咨询会话
curl -X POST http://localhost:8000/api/sessions/start \
  -H "Authorization: Bearer <access_token>"
# => 返回 session_id 与首条问候消息

# 4) 发送消息
curl -X POST http://localhost:8000/api/sessions/<session_id>/post_message \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"message":"最近有些焦虑，睡眠不好"}'
# => 返回 AI 回复与上下文更新
```

## 核心理念
我们希望心理支持「可信赖、随时可得且尊重隐私」。平台通过本地化部署与透明的数据流转，让用户掌握自己的信息；多智能体分工协作，保证专业性与成本平衡；功能层面更关注“连续陪伴”和“有效反馈”，而不仅是单轮问答。

## 多智能体架构
- **TherapistAgent**：主咨询对话，负责记忆提取、情绪识别、专业建议。
- **ClerkAgent**：Onboarding 画像生成、会话总结、关键事件更新，默认使用成本更优的 GPT-4o-mini。
- **Session Orchestrator**：协调对话流程、计时、轮次与提醒，保证一人一活跃会话。
- **Agno Agent Framework**：承担上下文、记忆、工具调用与持久化，默认读取 `.env` 中的配置，支持扩展新模型或工具。

## 记忆与数据
- **会话存储**：业务表（users/sessions 等）在 `public` schema，Agno 运行时数据（memories/sessions）在 `ai` schema。
- **自动记忆**：从对话中提取偏好、目标、困扰、关键事件，存入 JSONB 字段，按相关性自动加载。
- **隐私保障**：仅本地数据库持久化；调用 OpenAI 仅用于实时推理，不保留内容；支持导出/删除数据。

## 前端体验
- **技术栈**：Vue 3 + Vite + Tailwind + Vue Router + Axios。
- **核心页面**：登录注册、Onboarding 问卷、咨询对话、历史回顾、个人画像/洞察、管理员面板。
- **开发命令**：
  - 开发：`npm run dev`
  - 构建：`npm run build`
  - 预览：`npm run preview`
- **配置**：在 `frontend/src/api/axios.js` 设置后端 `baseURL`。

## 部署与运行
### 后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# 配置 .env（示例关键字段）
cat > .env <<'EOF'
DATABASE_URL=postgresql://ai_user:password@localhost/ai_therapy
SECRET_KEY=replace-me
OPENAI_API_KEY=sk-...
EOF

# 初始化数据库
alembic upgrade head
python scripts/init_agno_tables.py

# 启动
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 前端
```bash
cd frontend
npm install
npm run dev   # 本地开发
npm run build # 生产构建
```

## API 速览
- `GET /health`：健康检查。
- `POST /api/auth/register`：注册并返回 JWT。
- `POST /api/auth/login`：登录获取 JWT。
- `POST /api/sessions/start`：创建新会话（自动关闭旧会话）。
- `POST /api/sessions/{session_id}/post_message`：发送消息并获取回复。
- `POST /api/sessions/{session_id}/end`：结束会话并生成总结。
- `GET /api/sessions/history`：查看历史会话。
- `GET /api/onboarding/questions` / `POST /api/onboarding/answers`：Onboarding 问答流。
- 更多端点请参考 `backend/app/api/routes` 以及 `docs/guide.md`。

## 性能与优化
- **成本优化**：对总结与画像使用 GPT-4o-mini，对深度咨询使用 GPT-4o；可在 `.env` 中调整模型与温度。
- **记忆裁剪**：通过相关性检索与轮次上限，避免上下文膨胀；可调 `THERAPIST_HISTORY_RUNS`。
- **缓存与重用**：前端路由按需加载，组件状态由 Pinia 管理；后端会话查询使用 JSONB 统计避免全量展开。
- **跨端体验**：默认开启 CORS，前后端可独立部署。

## FAQ
### 数据会上传云端吗？
不会，所有数据写入本地 PostgreSQL。调用 OpenAI 仅用于即时推理，不持久化用户内容。

### 可以扩展新的 Agent 或模型吗？
可以。Agno 层支持自定义工具与模型配置，新增服务时在 `app/services` / `app/agents` 中扩展并在 orchestrator 中挂载即可。

### 如何快速验证环境？
启动后执行 `curl http://localhost:8000/health`；前端 `npm run dev` 后访问控制台首页即可。

## 路线图
- [ ] 语音对话与情绪声纹分析
- [ ] 多语言支持（英语/日语）
- [ ] 情绪趋势可视化与长期成长报告
- [ ] 移动端适配与推送提醒
- [ ] 咨询计划与干预建议模板

## 贡献与支持
- 欢迎提交 Issue、PR 或完善文档。请保持清晰的 commit 信息与必要的单元测试。
- 如需讨论需求或集成，请在 Issue 中提供背景与预期行为。

## 许可证
当前项目未正式发布许可证，使用前请与维护者确认。请遵守所在地域的法律法规，不得用于非法或不道德场景。
