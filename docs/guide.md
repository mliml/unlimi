# Agno 框架引入完整技术方案

> 生成时间：2025-12-08
> 版本：v1.0

## 目录

1. [技术框架](#一技术框架)
2. [文件变更清单](#二文件变更清单)
3. [技术方案详解](#三技术方案详解)
4. [需要确认的配置项](#四需要确认的-agno-框架配置项)
5. [总结](#总结)

---

## 一、技术框架

### 1.1 核心技术栈

```
后端框架: FastAPI
数据库: PostgreSQL (生产) / SQLite (开发)
AI 框架: Agno v2.0+
LLM 提供商: OpenAI (gpt-4o, gpt-4o-mini)
ORM: SQLAlchemy 2.0
认证: JWT (python-jose)
```

### 1.2 Agno 核心组件使用

| 组件 | 用途 | 说明 |
|------|------|------|
| **Agent** | 封装 Therapist 和 Clerk 两个智能体 | 替代原有的 TherapistAgent 和 ClerkAgent 类 |
| **Session** | 管理对话会话 | 自动持久化聊天历史和状态 |
| **Memory** | 存储用户长期记忆 | 替代原有的 UserPersona 表 |
| **Session State** | 管理会话级状态 | 存储 user_context 等临时数据 |
| **Tools** | 扩展 Agent 能力 | Clerk Agent 的数据库/文件操作 |
| **Database** | 持久化存储 | SqliteDb/PostgresDb |

### 1.3 架构分层

```
┌─────────────────────────────────────────────────────────┐
│                  API Layer (FastAPI)                     │
│  /sessions, /onboarding, /users, /admin                 │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│              Service Layer (业务逻辑)                    │
│  - TherapistAgentService (封装 Agno Therapist Agent)    │
│  - ClerkAgentService (封装 Agno Clerk Agent)            │
│  - SessionService (会话管理)                             │
└────────────────────┬────────────────────────────────────┘
                     │
      ┌──────────────┴──────────────┐
      │                             │
┌─────┴──────┐              ┌──────┴────────┐
│Agno Agents │              │Custom Database│
│            │              │                │
│- Therapist │              │- users         │
│- Clerk     │              │- user_contexts │
│            │              │- sessions      │
│Agno Tables:│              │- session_reviews│
│- sessions  │              └────────────────┘
│- messages  │
│- memories  │
└────────────┘
```

### 1.4 Memory 技术方案

#### Agno 内置 Memory vs Mem0 对比

| 方案 | 实现方式 | 数据存储 | 优势 | 劣势 |
|------|---------|---------|------|------|
| **Agno 内置 Memory** | `enable_user_memories=True` | 你的数据库 (`agno_memories` 表) | ✅ 数据自主可控<br>✅ 无额外服务<br>✅ 配置简单 | ⚠️ 功能相对基础 |
| **Mem0 集成** | `Mem0Tools()` | Mem0 托管平台 | ✅ 多模态支持<br>✅ 强大语义搜索<br>✅ 自动分类 | ❌ 需要额外 API Key<br>❌ 数据在第三方<br>❌ 增加成本 |

**最终方案**：使用 **Agno 内置 Memory**

理由：
1. 符合数据完全掌控的需求
2. 无需额外服务，降低架构复杂度
3. 足以满足当前用户画像存储需求
4. 可以随时升级到 Mem0（如果后续需要更强大功能）

---

## 二、文件变更清单

### 2.1 新增文件

```
app/services/
├── agno_agents/
│   ├── __init__.py
│   ├── therapist_agent_service.py    # TherapistAgent 封装
│   ├── clerk_agent_service.py        # ClerkAgent 封装
│   └── tools/                        # Clerk Agent 工具
│       ├── __init__.py
│       ├── user_context_tool.py      # 更新用户上下文
│       ├── session_review_tool.py    # 保存会话总结
│       └── database_tool.py          # 数据库操作（如需要）
│
app/db/models/
├── user_context.py                   # 新增：用户情况模型
│
app/config/prompts/
├── therapist_base_instructions.yaml  # Therapist 基础指令
├── therapist_context_template.yaml   # 用户上下文模板
├── clerk_base_instructions.yaml      # Clerk onboarding 指令
└── clerk_session_end_instructions.yaml# Clerk 会话结束指令

scripts/
├── migrate_to_agno.py                # 数据迁移脚本
└── verify_migration.py               # 数据验证脚本

guide.md                              # 本技术方案文档
```

### 2.2 修改文件

```
app/services/
├── llm_service.py                    # 【删除】
├── prompt_loader.py                  # 【保留】用于加载 prompts
├── user_understanding_service.py     # 【重构】使用 ClerkAgentService
│
app/agents/
├── therapist_agent.py                # 【删除】
├── clerk_agent.py                    # 【删除】
├── intent_classifier.py              # 【保留但暂停使用】
│
app/orchestrator/
├── session_orchestrator.py           # 【重构】使用新的 Agent Services
│
app/api/routes/
├── sessions.py                       # 【修改】使用新的 Service
├── onboarding.py                     # 【修改】使用新的 Service
├── users.py                          # 【修改】读取 Memory 替代 Persona
│
app/db/models/
├── user_persona.py                   # 【删除】由 Agno Memory 替代
├── user_prompt.py                    # 【删除】由 UserContext 替代
├── session_message.py                # 【删除】由 Agno Messages 替代
├── session.py                        # 【修改】只保留元数据
│
app/core/
├── config.py                         # 【修改】添加 Agno 配置
├── deps.py                           # 【修改】添加 Agent 依赖注入
│
requirements.txt                      # 【修改】添加 agno
alembic/versions/
└── XXXX_migrate_to_agno.py          # 【新增】数据迁移脚本
```

### 2.3 删除文件

```
app/agents/therapist_agent.py         # 由 TherapistAgentService 替代
app/agents/clerk_agent.py             # 由 ClerkAgentService 替代
app/services/llm_service.py           # 由 Agno 内置 LLM 调用替代
app/db/models/user_persona.py         # 由 Agno Memory 替代
app/db/models/user_prompt.py          # 由 UserContext 替代
app/db/models/session_message.py      # 由 Agno Messages 替代
```

---

## 三、技术方案详解

### 3.1 数据流向图

#### 3.1.1 Therapist Agent 对话流程

```
┌─────────────────────────────────────────────────────────┐
│  用户发送消息                                            │
│  POST /sessions/{session_id}/post_message              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────┐
│  SessionOrchestrator.process_message()                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────┐
│  TherapistAgentService.chat()                          │
│                                                         │
│  1. 从数据库加载 UserContext (一次性)                   │
│  2. 构造 session_state:                                 │
│     {                                                   │
│       "user_context": "用户情况与咨询目标...",          │
│       "user_id": 123                                    │
│     }                                                   │
│  3. 调用 agent.run()                                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────┐
│  Agno Therapist Agent                                   │
│                                                         │
│  自动执行：                                              │
│  1. 加载 session_state (从 agno_session_state 表)      │
│  2. 加载 chat history (从 agno_messages 表)            │
│     - num_history_runs=10 (最近10轮对话)               │
│  3. 加载 user memories (从 agno_memories 表)           │
│     - 自动检索相关记忆                                  │
│  4. 构建 Instructions:                                  │
│     """                                                 │
│     {base_instructions}                                 │
│                                                         │
│     ## 用户情况与咨询目标                                │
│     {session_state.user_context}                        │
│                                                         │
│     ## 已知用户信息                                      │
│     {memories}                                          │
│     """                                                 │
│  5. 调用 LLM 生成回复                                   │
│  6. 自动提取新的 user memories (如果启用)               │
│  7. 保存消息到 agno_messages                            │
│  8. 更新 session_state 到 agno_session_state           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────┐
│  返回回复给前端                                          │
└────────────────────────────────────────────────────────┘

数据存储位置：
┌──────────────────────┐
│ Custom Database      │
│ - user_contexts      │  ← 会话开始时加载一次
└──────────────────────┘

┌──────────────────────┐
│ Agno Tables          │
│ - agno_messages      │  ← 每条消息自动保存
│ - agno_memories      │  ← 自动提取用户信息
│ - agno_session_state │  ← 自动持久化 state
└──────────────────────┘
```

#### 3.1.2 Clerk Agent Onboarding 流程

```
┌─────────────────────────────────────────────────────────┐
│  用户提交 Onboarding 回答                                 │
│  POST /onboarding/submit                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────┐
│  ClerkAgentService.analyze_onboarding()                │
│                                                         │
│  1. 构造 prompt (包含用户回答)                           │
│  2. 调用 agent.run()                                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────┐
│  Agno Clerk Agent                                       │
│                                                         │
│  执行：                                                  │
│  1. 分析用户回答                                         │
│  2. 生成结构化 Markdown 格式的用户上下文                 │
│  3. 调用 Tool: save_user_context()                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────┐
│  Tool: save_user_context(user_id, context_markdown)    │
│                                                         │
│  保存到数据库:                                           │
│  UserContext.context_text = context_markdown            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────┐
│  返回成功，标记 user.has_finished_onboarding = True    │
└────────────────────────────────────────────────────────┘
```

#### 3.1.3 Clerk Agent 会话结束流程

```
┌─────────────────────────────────────────────────────────┐
│  用户结束会话                                            │
│  POST /sessions/{session_id}/end                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────┐
│  ClerkAgentService.process_session_end()               │
│                                                         │
│  1. 构造 prompt: "分析本次会话，更新用户上下文和生成总结"  │
│  2. 调用 agent.run(session_id=xxx, user_id=xxx)        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────┐
│  Agno Clerk Agent                                       │
│                                                         │
│  自动执行：                                              │
│  1. 加载本次会话的所有消息 (从 agno_messages)           │
│     - add_history_to_context=True 自动添加              │
│  2. 分析对话内容                                         │
│  3. 判断是否需要更新用户上下文                           │
│  4. 如需更新，调用 Tool: update_user_context()          │
│  5. 生成会话总结                                         │
│  6. 调用 Tool: save_session_review()                    │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ↓                     ↓
┌──────────────────┐  ┌──────────────────┐
│ Tool:            │  │ Tool:            │
│update_user_      │  │save_session_     │
│context()         │  │review()          │
│                  │  │                  │
│更新 UserContext  │  │保存 SessionReview│
│表                │  │表                │
└──────────────────┘  └──────────────────┘
```

#### 3.1.4 读取历史记录流程

```
┌─────────────────────────────────────────────────────────┐
│  前端请求历史消息                                         │
│  GET /sessions/{session_id}/get_messages               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────┐
│  SessionService.get_session_messages()                 │
│                                                         │
│  方案：使用 Agno API                                     │
│                                                         │
│  1. 通过 session_id 查找对应的 agno_session_id          │
│     (从 sessions 表)                                    │
│  2. 创建临时 AgentSession 对象                          │
│     session = AgentSession(                             │
│         session_id=agno_session_id,                     │
│         agent_id=therapist_agent.id,                    │
│         db=db                                           │
│     )                                                   │
│  3. 调用 session.get_chat_history()                     │
│     messages = session.get_chat_history()               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────┐
│  Agno 从 agno_messages 表查询                           │
│                                                         │
│  SELECT * FROM agno_messages                            │
│  WHERE session_id = ?                                   │
│  ORDER BY created_at ASC                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌────────────────────────────────────────────────────────┐
│  转换为前端格式并返回                                     │
│  [                                                      │
│    {                                                    │
│      "sender": "user",                                  │
│      "message": "...",                                  │
│      "created_at": "..."                                │
│    },                                                   │
│    ...                                                  │
│  ]                                                      │
└────────────────────────────────────────────────────────┘
```

### 3.2 数据库表结构变更

#### 3.2.1 迁移前后对比

**迁移前 (Current)**

```sql
-- 用户表 (保留)
users
├── id
├── email
├── hashed_password
├── has_finished_onboarding
├── created_at
└── updated_at

-- 用户提示词 (删除 → UserContext)
user_prompts
├── id
├── user_id
├── type (counselor/coach/...)
├── prompt  ← 完整的 counselor prompt
├── created_at
└── updated_at

-- 用户画像 (删除 → agno_memories)
user_personas
├── id
├── user_id
├── content
├── confidence (high/medium/low)
├── source (onboarding/clerk)
└── updated_at

-- 会话 (简化，只保留元数据)
sessions
├── id
├── user_id
├── start_time
├── end_time
└── status

-- 会话消息 (删除 → agno_messages)
session_messages
├── id
├── session_id
├── sender (user/therapist/system)
├── message
└── created_at

-- 会话总结 (保留)
session_reviews
├── id
├── session_id
├── message_review
├── key_events (JSON)
└── created_at
```

**迁移后 (New)**

```sql
-- 用户表 (不变)
users
├── id
├── email
├── hashed_password
├── has_finished_onboarding
├── created_at
└── updated_at

-- 【新增】用户情况与咨询目标
user_contexts
├── id
├── user_id (UNIQUE)
├── context_text (TEXT) ← 结构化 Markdown
├── created_at
└── updated_at

-- 会话元数据 (添加 agno_session_id)
sessions
├── id
├── user_id
├── agno_session_id (VARCHAR) ← 关联 Agno session
├── start_time
├── end_time
└── status

-- 会话总结 (不变)
session_reviews
├── id
├── session_id
├── message_review
├── key_events (JSON)
└── created_at

-- 【Agno 自动创建】
agno_sessions
├── session_id (PK)
├── session_name
├── session_data (JSONB)  ← 包含 session_state
├── user_id
├── agent_id
├── created_at
└── updated_at

agno_messages
├── id (PK)
├── session_id
├── agent_id
├── role (user/assistant/system)
├── content
├── metadata (JSONB)
├── created_at
└── ...

agno_memories
├── memory_id (PK)
├── memory (TEXT)
├── user_id
├── agent_id
├── topics (JSON)
├── created_at
└── updated_at
```

#### 3.2.2 数据迁移策略

**阶段 1: Schema 迁移**

```python
# alembic/versions/XXXX_migrate_to_agno.py

def upgrade():
    # 1. 创建新表
    op.create_table(
        'user_contexts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('context_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )

    # 2. 修改 sessions 表
    op.add_column('sessions', sa.Column('agno_session_id', sa.String(255), nullable=True))
    op.create_index('ix_sessions_agno_session_id', 'sessions', ['agno_session_id'])

    # 注意：暂不删除旧表，等数据迁移完成后再删除


def downgrade():
    op.drop_index('ix_sessions_agno_session_id', 'sessions')
    op.drop_column('sessions', 'agno_session_id')
    op.drop_table('user_contexts')
```

**阶段 2: 数据迁移脚本**

```python
# scripts/migrate_to_agno.py

from sqlalchemy.orm import Session
from app.db.models.user_prompt import UserPrompt, PromptType
from app.db.models.user_persona import UserPersona
from app.db.models.session_message import SessionMessage
from app.db.models.user_context import UserContext
from app.services.agno_agents.therapist_agent_service import TherapistAgentService
import re

def migrate_user_prompts_to_contexts(db: Session):
    """
    迁移 user_prompts → user_contexts
    提取 counselor prompt 中的用户个性化信息部分
    """
    prompts = db.query(UserPrompt).filter(
        UserPrompt.type == PromptType.counselor
    ).all()

    for prompt in prompts:
        # 从完整 prompt 中提取用户个性化部分
        # 假设格式：
        # {base_prompt}
        # ## 用户个性化信息
        # {user_context}
        # ---
        # 用户原始回答：...

        match = re.search(
            r'## 用户个性化信息\n\n(.*?)\n\n---',
            prompt.prompt,
            re.DOTALL
        )

        if match:
            context_text = match.group(1).strip()
        else:
            # 如果没有找到，使用整个 prompt（保底）
            context_text = f"# 用户情况\n\n{prompt.prompt[:500]}"

        # 创建 UserContext
        user_context = UserContext(
            user_id=prompt.user_id,
            context_text=context_text
        )
        db.add(user_context)

    db.commit()
    print(f"✓ 迁移了 {len(prompts)} 个用户上下文")


def migrate_personas_to_memories(db: Session, agno_db):
    """
    迁移 user_personas → agno_memories
    """
    from agno.storage.memory import Memory

    personas = db.query(UserPersona).all()
    therapist_agent = TherapistAgentService().agent

    for persona in personas:
        # 创建 Memory 对象
        memory = Memory(
            memory=persona.content,
            user_id=str(persona.user_id),
            agent_id=therapist_agent.id,
            topics=[persona.source.value],  # onboarding/clerk
            metadata={
                "confidence": persona.confidence.value,
                "source": persona.source.value,
                "migrated_from": "user_personas",
                "original_id": persona.id
            }
        )

        # 保存到 Agno 数据库
        agno_db.upsert_memory(memory)

    print(f"✓ 迁移了 {len(personas)} 条用户记忆")


def migrate_session_messages_to_agno(db: Session, therapist_service):
    """
    迁移 session_messages → agno_messages
    """
    from app.db.models.session import Session as SessionModel

    sessions = db.query(SessionModel).all()

    for session in sessions:
        # 为每个 session 创建 Agno session
        messages = db.query(SessionMessage).filter(
            SessionMessage.session_id == session.id
        ).order_by(SessionMessage.created_at.asc()).all()

        if not messages:
            continue

        # 创建 Agno session ID
        agno_session_id = f"migrated_{session.id}"

        # 模拟对话以创建 Agno session 和 messages
        for i, msg in enumerate(messages):
            if msg.sender.value == "user":
                # 用户消息 → 调用 agent.run()
                therapist_service.agent.run(
                    message=msg.message,
                    user_id=str(session.user_id),
                    session_id=agno_session_id,
                    stream=False
                )
            elif msg.sender.value == "therapist":
                # 治疗师消息 → 手动插入（不调用 LLM）
                from agno.models.message import Message
                from agno.models.message import Role

                assistant_msg = Message(
                    role=Role.ASSISTANT,
                    content=msg.message,
                    created_at=msg.created_at
                )

                # 直接插入数据库
                therapist_service.agent.db.upsert_message(
                    session_id=agno_session_id,
                    message=assistant_msg
                )

        # 更新 sessions 表的 agno_session_id
        session.agno_session_id = agno_session_id
        db.commit()

        print(f"✓ 迁移了 session {session.id} 的 {len(messages)} 条消息")


def main():
    """执行完整迁移"""
    from app.db.database import SessionLocal, engine
    from app.services.agno_agents.therapist_agent_service import TherapistAgentService

    db = SessionLocal()
    therapist_service = TherapistAgentService()

    try:
        print("开始数据迁移...")

        print("\n1. 迁移用户上下文...")
        migrate_user_prompts_to_contexts(db)

        print("\n2. 迁移用户画像到 Memory...")
        migrate_personas_to_memories(db, therapist_service.agent.db)

        print("\n3. 迁移会话消息...")
        migrate_session_messages_to_agno(db, therapist_service)

        print("\n✅ 数据迁移完成！")

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
```

**阶段 3: 验证与清理**

```python
# scripts/verify_migration.py

def verify_migration(db: Session):
    """验证数据迁移完整性"""

    # 1. 检查 UserContext 数量
    context_count = db.query(UserContext).count()
    old_prompt_count = db.query(UserPrompt).filter(
        UserPrompt.type == PromptType.counselor
    ).count()
    assert context_count == old_prompt_count, "UserContext 数量不匹配"

    # 2. 检查 Memory 数量
    memory_count = agno_db.count_memories()
    persona_count = db.query(UserPersona).count()
    assert memory_count >= persona_count, "Memory 数量不足"

    # 3. 检查 Session 关联
    sessions_with_agno_id = db.query(Session).filter(
        Session.agno_session_id.isnot(None)
    ).count()
    sessions_with_messages = db.query(Session).join(SessionMessage).distinct().count()
    assert sessions_with_agno_id == sessions_with_messages, "Session 关联不完整"

    print("✅ 数据验证通过")


def cleanup_old_tables(db: Session):
    """清理旧表（谨慎操作）"""
    # 备份后执行
    op.drop_table('user_personas')
    op.drop_table('user_prompts')
    op.drop_table('session_messages')
    print("✅ 旧表已删除")
```

### 3.3 核心代码实现

#### 3.3.1 TherapistAgentService

```python
# app/services/agno_agents/therapist_agent_service.py

from agno.agent import Agent
from agno.db.postgres import PostgresDb  # 或 SqliteDb
from agno.models.openai import OpenAIChat
from app.core.config import settings
from app.db.models.user_context import UserContext
from sqlalchemy.orm import Session
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TherapistAgentService:
    """
    Therapist Agent 服务封装
    负责管理治疗师 AI Agent 的生命周期和交互
    """

    _instance: Optional['TherapistAgentService'] = None
    _agent: Optional[Agent] = None

    def __new__(cls):
        """单例模式，确保全局只有一个 Agent 实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._agent is not None:
            return

        # 初始化 Agno 数据库连接
        if settings.DATABASE_URL.startswith("postgresql"):
            self.agno_db = PostgresDb(db_url=settings.DATABASE_URL)
        else:
            self.agno_db = SqliteDb(db_file=settings.SQLITE_DB_FILE)

        # 加载基础指令
        base_instructions = self._load_base_instructions()

        # 创建 Therapist Agent
        self._agent = Agent(
            name="TherapistAgent",
            model=OpenAIChat(
                id="gpt-4o",
                api_key=settings.OPENAI_API_KEY
            ),
            db=self.agno_db,

            # ===== Memory 配置 =====
            enable_user_memories=True,  # 自动提取用户事实

            # ===== Chat History 配置 =====
            add_history_to_context=True,  # 自动添加历史到上下文
            num_history_runs=10,  # 最近10轮对话

            # ===== Session State 配置 =====
            session_state={},  # 初始为空，运行时动态设置

            # ===== Instructions =====
            instructions=base_instructions + """

## 当前用户情况

{user_context}

## 已知用户信息

{memories}
""",

            # ===== 其他配置 =====
            markdown=True,
            show_tool_calls=False,
            resolve_in_context=True,  # 在指令中解析变量
        )

        logger.info("✓ TherapistAgent 初始化完成")

    @property
    def agent(self) -> Agent:
        """获取 Agent 实例"""
        return self._agent

    def chat(
        self,
        user_id: int,
        session_id: str,
        message: str,
        db: Session
    ) -> str:
        """
        处理用户消息

        Args:
            user_id: 用户ID
            session_id: 会话ID（对应 sessions.agno_session_id）
            message: 用户消息
            db: SQLAlchemy session (用于查询 UserContext)

        Returns:
            AI 回复文本
        """
        # 1. 加载用户上下文
        user_context = self._load_user_context(user_id, db)

        # 2. 构造 session_state
        # 注意：Agno 会自动持久化 session_state，下次运行时会加载
        session_state = {
            "user_context": user_context,
            "user_id": user_id,
        }

        # 3. 调用 Agent
        response = self._agent.run(
            message=message,
            user_id=str(user_id),  # Agno 使用字符串 user_id
            session_id=session_id,
            session_state=session_state,  # 传递 state
            stream=False
        )

        # 4. 返回回复内容
        return response.content

    def _load_user_context(self, user_id: int, db: Session) -> str:
        """从数据库加载用户上下文"""
        ctx = db.query(UserContext).filter_by(user_id=user_id).first()

        if ctx:
            return ctx.context_text
        else:
            return "（用户尚未完成初始评估）"

    def _load_base_instructions(self) -> str:
        """加载基础治疗师指令"""
        from app.services.prompt_loader import PromptLoader
        loader = PromptLoader()
        return loader.get_prompt("therapist_base_instructions.yaml")

    def get_user_memories(self, user_id: int) -> list:
        """
        获取用户的所有记忆（用于前端展示）

        Returns:
            [
                {
                    "memory": "用户喜欢户外活动",
                    "topics": ["interests"],
                    "updated_at": "2025-12-08"
                },
                ...
            ]
        """
        memories = self._agent.get_user_memories(user_id=str(user_id))

        return [
            {
                "memory": m.memory,
                "topics": m.topics,
                "updated_at": m.updated_at.isoformat() if m.updated_at else None
            }
            for m in memories
        ]
```

#### 3.3.2 ClerkAgentService

```python
# app/services/agno_agents/clerk_agent_service.py

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.run_context import RunContext
from app.core.config import settings
from app.db.models.user_context import UserContext
from app.db.models.session_review import SessionReview
from sqlalchemy.orm import Session
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ClerkAgentService:
    """Clerk Agent 服务封装"""

    _instance: Optional['ClerkAgentService'] = None
    _agent: Optional[Agent] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._agent is not None:
            return

        # 使用与 Therapist 相同的数据库
        from app.services.agno_agents.therapist_agent_service import TherapistAgentService
        therapist_service = TherapistAgentService()

        # 创建 Clerk Agent
        self._agent = Agent(
            name="ClerkAgent",
            model=OpenAIChat(
                id="gpt-4o",
                api_key=settings.OPENAI_API_KEY
            ),
            db=therapist_service.agno_db,

            # ===== Clerk 不需要 Memory =====
            enable_user_memories=False,

            # ===== 但需要访问历史记录 =====
            add_history_to_context=True,  # 自动添加会话历史

            # ===== Tools =====
            tools=[
                self._create_save_user_context_tool(),
                self._create_update_user_context_tool(),
                self._create_save_session_review_tool(),
            ],

            # ===== Instructions =====
            instructions=self._load_clerk_instructions(),

            markdown=True,
            show_tool_calls=False,
        )

        logger.info("✓ ClerkAgent 初始化完成")

    @property
    def agent(self) -> Agent:
        return self._agent

    def analyze_onboarding(
        self,
        user_id: int,
        answers: dict,
        db: Session
    ) -> str:
        """
        分析 onboarding 回答，生成用户上下文

        Args:
            user_id: 用户ID
            answers: {"main_goal": "...", "recent_concern": "...", "preferred_style": "..."}
            db: SQLAlchemy session

        Returns:
            生成的用户上下文文本
        """
        # 注入 db 到工具的上下文
        self._agent.session_state = {"db": db, "user_id": user_id}

        prompt = f"""
请根据用户的 onboarding 回答，生成用户基本情况与咨询目标。

用户回答：
- 咨询目标：{answers.get('main_goal', '未提供')}
- 近期困扰：{answers.get('recent_concern', '未提供')}
- 偏好风格：{answers.get('preferred_style', '未提供')}

要求：
1. 生成结构化 Markdown 格式
2. 包含以下部分：
   - ## 咨询目标
   - ## 当前困扰
   - ## 偏好风格
   - ## 综合评估
3. 长度控制在 200-400 字
4. 使用第三人称描述

生成后，请调用 `save_user_context` 工具保存。
"""

        response = self._agent.run(
            message=prompt,
            user_id=str(user_id),
            session_id=f"onboarding_{user_id}",
            stream=False
        )

        # 从数据库读取保存的上下文（由工具保存）
        ctx = db.query(UserContext).filter_by(user_id=user_id).first()
        return ctx.context_text if ctx else response.content

    def process_session_end(
        self,
        user_id: int,
        session_id: str,
        agno_session_id: str,
        db: Session
    ) -> dict:
        """
        会话结束时处理

        Args:
            user_id: 用户ID
            session_id: 业务 session ID (sessions.id)
            agno_session_id: Agno session ID (sessions.agno_session_id)
            db: SQLAlchemy session

        Returns:
            {
                "session_review": "...",
                "key_events": ["...", "..."],
                "context_updated": True/False
            }
        """
        # 注入 db 到工具上下文
        self._agent.session_state = {
            "db": db,
            "user_id": user_id,
            "session_id": session_id
        }

        prompt = """
请完成以下任务：

1. 分析本次咨询对话，生成会话总结：
   - 主要讨论的话题
   - 用户的情绪变化
   - 关键事件（2-5个关键时刻）

2. 判断是否需要更新用户上下文：
   - 如果发现用户的咨询目标、困扰或偏好有变化
   - 或者了解到新的重要信息
   - 则调用 `update_user_context` 工具更新

3. 调用 `save_session_review` 工具保存会话总结

请逐步执行。
"""

        response = self._agent.run(
            message=prompt,
            user_id=str(user_id),
            session_id=agno_session_id,
            stream=False
        )

        # 从数据库读取保存的结果
        review = db.query(SessionReview).filter_by(session_id=session_id).first()

        return {
            "session_review": review.message_review if review else "生成失败",
            "key_events": review.key_events if review else [],
            "context_updated": "update_user_context" in response.content  # 简单判断
        }

    # ===== 工具定义 =====

    def _create_save_user_context_tool(self):
        """创建保存用户上下文的工具"""
        def save_user_context(
            run_context: RunContext,
            context_markdown: str
        ) -> str:
            """
            保存用户上下文到数据库

            Args:
                context_markdown: 结构化 Markdown 格式的用户上下文
            """
            db = run_context.session_state.get("db")
            user_id = run_context.session_state.get("user_id")

            if not db or not user_id:
                return "错误：缺少数据库连接或用户ID"

            # 检查是否已存在
            ctx = db.query(UserContext).filter_by(user_id=user_id).first()

            if ctx:
                return "错误：用户上下文已存在，请使用 update_user_context"

            # 创建新记录
            ctx = UserContext(
                user_id=user_id,
                context_text=context_markdown
            )
            db.add(ctx)
            db.commit()

            logger.info(f"✓ 保存用户 {user_id} 的上下文")
            return f"✓ 用户上下文已保存（{len(context_markdown)} 字）"

        return save_user_context

    def _create_update_user_context_tool(self):
        """创建更新用户上下文的工具"""
        def update_user_context(
            run_context: RunContext,
            new_context_markdown: str
        ) -> str:
            """
            更新用户上下文

            Args:
                new_context_markdown: 新的用户上下文（完整替换）
            """
            db = run_context.session_state.get("db")
            user_id = run_context.session_state.get("user_id")

            if not db or not user_id:
                return "错误：缺少数据库连接或用户ID"

            ctx = db.query(UserContext).filter_by(user_id=user_id).first()

            if not ctx:
                return "错误：用户上下文不存在，请先完成 onboarding"

            # 更新
            ctx.context_text = new_context_markdown
            from datetime import datetime
            ctx.updated_at = datetime.utcnow()
            db.commit()

            logger.info(f"✓ 更新用户 {user_id} 的上下文")
            return "✓ 用户上下文已更新"

        return update_user_context

    def _create_save_session_review_tool(self):
        """创建保存会话总结的工具"""
        def save_session_review(
            run_context: RunContext,
            session_review: str,
            key_events: list[str]
        ) -> str:
            """
            保存会话总结

            Args:
                session_review: 会话总结文本
                key_events: 关键事件列表
            """
            db = run_context.session_state.get("db")
            session_id = run_context.session_state.get("session_id")

            if not db or not session_id:
                return "错误：缺少数据库连接或会话ID"

            review = SessionReview(
                session_id=session_id,
                message_review=session_review,
                key_events=key_events
            )
            db.add(review)
            db.commit()

            logger.info(f"✓ 保存会话 {session_id} 的总结")
            return f"✓ 会话总结已保存（{len(key_events)} 个关键事件）"

        return save_session_review

    def _load_clerk_instructions(self) -> str:
        """加载 Clerk 指令"""
        from app.services.prompt_loader import PromptLoader
        loader = PromptLoader()
        return loader.get_prompt("clerk_base_instructions.yaml")
```

#### 3.3.3 UserContext 模型

```python
# app/db/models/user_context.py

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class UserContext(Base):
    """
    用户基本情况与咨询目标

    存储结构化 Markdown 格式的用户上下文，
    用于每次会话时加载到 session_state
    """
    __tablename__ = "user_contexts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    context_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="context")
```

---

## 四、需要确认的 Agno 框架配置项

### 4.1 Therapist Agent 配置

| 配置项 | 当前建议值 | 说明 | 需要确认 |
|--------|-----------|------|---------|
| **model** | `gpt-4o` | LLM 模型 | ✅ 是否使用 gpt-4o？还是 gpt-4o-mini（成本更低）？ |
| **enable_user_memories** | `True` | 自动提取用户事实 | ✅ 是否启用自动 memory 提取？ |
| **num_history_runs** | `10` | 自动添加最近 N 轮对话 | ✅ 10 轮是否合适？（影响上下文成本） |
| **num_history_messages** | `未设置` | 更细粒度的消息数控制 | ⚠️ 是否需要设置？（如只取最近20条消息） |
| **markdown** | `True` | 支持 Markdown 格式回复 | ⚠️ 前端是否支持 Markdown 渲染？ |
| **show_tool_calls** | `False` | 是否在回复中显示工具调用 | ✅ 用户不应看到工具调用细节 |
| **resolve_in_context** | `True` | 在指令中解析变量（如 {user_context}） | ✅ 必须启用以使用动态指令 |
| **temperature** | `0.7` (模型默认) | LLM 温度参数 | ⚠️ 是否需要调整？（0.7 较平衡） |
| **max_tokens** | `2000` (模型默认) | 最大回复长度 | ⚠️ 治疗师回复通常多长？ |

### 4.2 Clerk Agent 配置

| 配置项 | 当前建议值 | 说明 | 需要确认 |
|--------|-----------|------|---------|
| **model** | `gpt-4o` | LLM 模型 | ✅ Clerk 是否需要用 gpt-4o？可以降级为 gpt-4o-mini 节省成本 |
| **enable_user_memories** | `False` | Clerk 不需要记忆 | ✅ 确认 Clerk 只处理任务，不存储记忆 |
| **add_history_to_context** | `True` | 读取会话历史（用于生成总结） | ✅ 必须启用以分析整个对话 |
| **temperature** | `0` | Clerk 需要稳定输出 | ✅ 生成总结应该更确定性 |

### 4.3 数据库配置

| 配置项 | 当前建议值 | 说明 | 需要确认 |
|--------|-----------|------|---------|
| **db_url** | `从 settings.DATABASE_URL 读取` | 数据库连接 | ✅ 使用现有数据库配置 |
| **table_name** | `agno_sessions` (默认) | Agno session 表名 | ⚠️ 是否需要自定义表名前缀？ |
| **auto_create_tables** | `True` (默认) | 自动创建 Agno 表 | ✅ 首次运行时自动创建 |

### 4.4 Session State 配置

| 配置项 | 当前建议值 | 说明 | 需要确认 |
|--------|-----------|------|---------|
| **session_state 初始值** | `{}` | Agent 初始化时为空 | ✅ 运行时动态设置 |
| **user_context 加载时机** | 每次 `agent.run()` 时加载 | 从数据库读取 UserContext | ⚠️ 是否缓存？还是每次都查数据库？ |
| **session_state 持久化** | 自动 (Agno 负责) | 保存到 `agno_session_state` | ✅ 无需额外配置 |

### 4.5 Memory 配置

| 配置项 | 当前建议值 | 说明 | 需要确认 |
|--------|-----------|------|---------|
| **enable_user_memories** | `True` | 使用 Agno 内置 memory | ✅ 确认不使用 Mem0 |
| **memory_table_name** | `agno_memories` (默认) | Memory 存储表名 | ⚠️ 是否需要自定义？ |
| **自动提取频率** | 每次对话后 | Agno 自动判断并提取 | ✅ 无需配置 |
| **前端展示** | 调用 `agent.get_user_memories()` | 读取用户画像 | ⚠️ 是否需要过滤或格式化？ |

### 4.6 Prompt 配置

#### Therapist Agent Base Instructions

```yaml
# app/config/prompts/therapist_base_instructions.yaml

system_prompt: |
  你是一位专业的心理咨询师，具有丰富的临床经验和共情能力。

  ## 核心原则

  1. **倾听与理解**：认真倾听来访者的诉说，理解其情绪和需求
  2. **非评判性**：不对来访者的想法和行为进行评判
  3. **保密性**：尊重来访者的隐私，保护咨询内容的保密性
  4. **专业边界**：保持专业关系，不提供医疗诊断或药物建议
  5. **人本主义**：相信来访者有自我成长和解决问题的能力

  ## 咨询风格

  - 使用温和、支持性的语言
  - 提问开放性问题，鼓励来访者表达
  - 适时反馈和总结，帮助来访者澄清思绪
  - 长度控制在 100-200 字，避免过长回复
  - 使用简体中文

  ## 重要提醒

  - 如果来访者表达自杀或自残意图，请立即表达关切并建议寻求专业紧急帮助
  - 不要提供具体的医疗诊断或药物建议
  - 如果超出咨询范围，建议来访者寻求专业医疗帮助
```

**需要确认**：
- ✅ 回复长度 100-200 字是否合适？
- ✅ 是否需要调整咨询风格（如更直接、更支持性等）？
- ✅ 是否需要添加特定场景的处理指引？

#### Clerk Agent Instructions

```yaml
# app/config/prompts/clerk_base_instructions.yaml

system_prompt: |
  你是一位心理咨询助理，负责处理咨询的行政和分析工作。

  ## 主要职责

  1. **Onboarding 分析**：
     - 分析用户的初始评估回答
     - 生成结构化的用户情况描述（Markdown 格式）
     - 提取用户的咨询目标、困扰和偏好

  2. **会话总结**：
     - 分析整个咨询对话
     - 总结主要讨论内容和情绪变化
     - 提取 2-5 个关键事件

  3. **用户情况更新**：
     - 根据新的对话内容判断是否需要更新用户情况
     - 如有重要变化，更新用户上下文

  ## 输出要求

  - 使用结构化 Markdown 格式
  - 简洁专业，避免冗余
  - 使用第三人称描述
  - 准确调用工具函数
```

**需要确认**：
- ✅ Clerk 的职责范围是否清晰？
- ⚠️ 是否需要添加其他工具（如导出报告、数据分析等）？
- ✅ 用户上下文更新的判断标准是否需要更明确？

### 4.7 性能与成本配置

| 配置项 | 影响 | 建议值 | 需要确认 |
|--------|------|--------|---------|
| **History 长度** | Token 消耗 | 10 轮 ≈ 2000-4000 tokens | ⚠️ 根据预算调整 |
| **Model 选择** | 成本与质量 | gpt-4o (高质量) vs gpt-4o-mini (低成本) | ✅ Therapist 用 4o，Clerk 可用 mini |
| **Memory 自动提取** | API 调用次数 | 每次对话后 | ⚠️ 是否需要限制提取频率？ |
| **Session State 大小** | 数据库存储 | <10KB/session | ✅ 当前设计满足 |

### 4.8 部署与环境配置

```python
# app/core/config.py

class Settings(BaseSettings):
    # === 现有配置 ===
    DATABASE_URL: str
    OPENAI_API_KEY: str

    # === 新增 Agno 配置 ===

    # Agno 数据库（默认使用主数据库）
    AGNO_DB_URL: str = None  # 如果为空，使用 DATABASE_URL

    # Therapist Agent 配置
    THERAPIST_MODEL: str = "gpt-4o"
    THERAPIST_HISTORY_RUNS: int = 10
    THERAPIST_ENABLE_MEMORY: bool = True

    # Clerk Agent 配置
    CLERK_MODEL: str = "gpt-4o-mini"  # Clerk 可以使用更便宜的模型
    CLERK_TEMPERATURE: float = 0.0

    # 性能配置
    AGNO_AUTO_CREATE_TABLES: bool = True
    AGNO_MEMORY_TABLE_PREFIX: str = "agno_"

    @property
    def agno_database_url(self) -> str:
        """获取 Agno 数据库 URL"""
        return self.AGNO_DB_URL or self.DATABASE_URL
```

**需要确认**：
- ✅ 是否需要将 Agno 表放在单独的数据库？
- ✅ 表名前缀 `agno_` 是否满意？
- ⚠️ 是否需要区分开发/生产环境配置？

---

## 五、关键决策总结

### 🔴 需要你立即确认的配置

1. **LLM 模型选择**：
   - Therapist: `gpt-4o` 还是 `gpt-4o-mini`？
   - Clerk: `gpt-4o` 还是 `gpt-4o-mini`？

2. **History 长度**：
   - 当前设置 10 轮对话，约 2000-4000 tokens/请求
   - 是否需要调整？（影响成本和上下文质量）

3. **Memory 方案**：
   - 确认使用 **Agno 内置 Memory**（不使用 Mem0）

4. **UserContext 加载策略**：
   - 每次对话都从数据库读取？
   - 还是会话级缓存？

5. **Markdown 支持**：
   - 前端是否支持 Markdown 渲染？
   - 还是需要纯文本回复？

6. **数据迁移时机**：
   - 是否需要保留历史数据？
   - 迁移计划时间？

### ✅ 推荐配置（可直接采用）

```python
# 推荐配置
THERAPIST_CONFIG = {
    "model": "gpt-4o",  # 高质量对话体验
    "num_history_runs": 10,  # 保留最近10轮
    "enable_user_memories": True,  # 自动提取用户信息
    "markdown": True,  # 支持 Markdown（需前端配合）
    "temperature": 0.7,  # 平衡创造性和稳定性
}

CLERK_CONFIG = {
    "model": "gpt-4o-mini",  # 节省成本，任务型场景足够
    "temperature": 0.0,  # 确定性输出
    "enable_user_memories": False,  # Clerk 不需要记忆
}

DATABASE_CONFIG = {
    "use_same_db": True,  # Agno 表和业务表在同一数据库
    "table_prefix": "agno_",  # 清晰区分 Agno 表
    "auto_create_tables": True,  # 自动创建表
}
```

---

## 总结

### 📋 完整方案包含

1. **技术框架**：核心技术栈、Agno 组件使用、架构分层图
2. **文件变更清单**：新增/修改/删除文件的详细列表
3. **详细技术方案**：
   - 4 个完整的数据流向图
   - 数据库表结构变更对比
   - 3 阶段数据迁移方案（Schema → 数据 → 验证清理）
   - 核心代码实现（TherapistAgentService 和 ClerkAgentService）
4. **需要确认的配置项**：8 个配置类别，涵盖所有关键决策点

### 🔑 关键技术点

1. **Agno Memory**：使用内置 memory（非 Mem0），数据存储在你的数据库
2. **Session State**：每次对话时从数据库加载 UserContext，自动持久化
3. **Chat History**：完全由 Agno 管理，使用 `AgentSession.get_chat_history()` 读取
4. **Tools**：Clerk Agent 通过工具操作数据库（save/update UserContext, save SessionReview）

### ⚠️ 等待你确认的关键配置

1. **LLM 模型**：Therapist 和 Clerk 分别用什么模型？
2. **History 长度**：10 轮对话是否合适？
3. **UserContext 加载**：每次查询 DB 还是缓存？
4. **Markdown 支持**：前端是否支持渲染？
5. **数据迁移**：何时执行迁移？

---

## 参考资料

- [Agno 官方文档](https://docs.agno.com/introduction)
- [Agno Memory 文档](https://docs.agno.com/agents/memory)
- [Agno State 管理](https://docs.agno.com/basics/state/overview)
- [Agno Chat History](https://docs.agno.com/basics/chat-history/agent/overview)
- [Mem0 集成文档](https://docs.mem0.ai/integrations/agno)
- [Agno GitHub](https://github.com/agno-agi/agno)

---

**文档生成时间**: 2025-12-08
**版本**: v1.0
**状态**: 待确认配置项
