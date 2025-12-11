"""
数据迁移脚本：将旧数据迁移到 Agno 框架

迁移内容：
1. user_prompts -> user_contexts (转换为结构化 Markdown)
2. user_personas -> Agno memories (通过 TherapistAgent API)
3. session_messages -> Agno messages (需要先生成 agno_session_id)

使用方法：
    python scripts/migrate_to_agno.py [--dry-run]
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session as DBSession
from sqlalchemy import text
from app.db.database import get_db
from app.db.models.user_prompt import UserPrompt, PromptType
from app.db.models.user_persona import UserPersona
from app.db.models.session_message import SessionMessage, MessageSender
from app.db.models.session import Session as SessionModel
from app.db.models.user_context import UserContext
from app.db.models.user import User
from app.agents.therapist_agent_service import TherapistAgentService
from datetime import datetime
import logging
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_user_prompts_to_contexts(db: DBSession, dry_run: bool = False):
    """
    迁移 user_prompts 到 user_contexts

    将 counselor_prompt 转换为结构化 Markdown 格式的 UserContext
    """
    logger.info("=" * 60)
    logger.info("开始迁移 user_prompts -> user_contexts")
    logger.info("=" * 60)

    # 查询所有 counselor_prompt
    prompts = db.query(UserPrompt).filter(
        UserPrompt.type == PromptType.counselor
    ).all()

    logger.info(f"找到 {len(prompts)} 个用户 prompts")

    migrated = 0
    skipped = 0

    for prompt in prompts:
        # 检查是否已经存在 user_context
        existing_context = db.query(UserContext).filter_by(
            user_id=prompt.user_id
        ).first()

        if existing_context:
            logger.info(f"  [SKIP] 用户 {prompt.user_id} 已有 UserContext")
            skipped += 1
            continue

        # 转换为结构化 Markdown
        context_text = f"""# 用户基本情况与咨询目标

## 用户画像
{prompt.prompt}

## 备注
本信息从旧版 user_prompts 表迁移而来（迁移时间：{datetime.utcnow().isoformat()}）
"""

        if not dry_run:
            new_context = UserContext(
                user_id=prompt.user_id,
                context_text=context_text,
                created_at=prompt.created_at,
                updated_at=prompt.updated_at
            )
            db.add(new_context)
            db.commit()
            logger.info(f"  [OK] 用户 {prompt.user_id} UserContext 创建成功")
        else:
            logger.info(f"  [DRY-RUN] 将为用户 {prompt.user_id} 创建 UserContext")

        migrated += 1

    logger.info(f"\n迁移完成：成功 {migrated} 个，跳过 {skipped} 个")
    return migrated, skipped


def migrate_personas_to_memories(db: DBSession, dry_run: bool = False):
    """
    迁移 user_personas 到 Agno memories

    通过 TherapistAgent.add_memory() 添加到 Agno 框架
    """
    logger.info("=" * 60)
    logger.info("开始迁移 user_personas -> Agno memories")
    logger.info("=" * 60)

    # 查询所有 personas
    personas = db.query(UserPersona).all()

    logger.info(f"找到 {len(personas)} 个用户 personas")

    if dry_run:
        logger.info("[DRY-RUN] 跳过实际迁移")
        return 0, 0

    # 初始化 TherapistAgent 获取 agno_db
    therapist_service = TherapistAgentService()
    agno_db = therapist_service.agno_db

    # 按用户分组
    user_personas = {}
    for persona in personas:
        if persona.user_id not in user_personas:
            user_personas[persona.user_id] = []
        user_personas[persona.user_id].append(persona)

    migrated = 0

    for user_id, personas_list in user_personas.items():
        logger.info(f"\n处理用户 {user_id}（{len(personas_list)} 个 personas）")

        for persona in personas_list:
            try:
                # 使用 PostgresDb 直接插入 memory
                from agno.db.schemas.memory import UserMemory
                import time
                import uuid

                memory_obj = UserMemory(
                    memory=persona.content,
                    memory_id=str(uuid.uuid4()),
                    user_id=str(user_id),
                    topics=["migration", "persona"],
                    created_at=int(persona.updated_at.timestamp()) if hasattr(persona, 'updated_at') and persona.updated_at else int(time.time())
                )

                agno_db.upsert_user_memory(memory_obj)

                logger.info(f"  [OK] 添加 memory: {persona.content[:50]}...")
                migrated += 1

            except Exception as e:
                logger.error(f"  [ERROR] 添加 memory 失败: {e}")

    logger.info(f"\n迁移完成：成功 {migrated} 个")
    return migrated, 0


def migrate_session_messages_to_agno(db: DBSession, dry_run: bool = False):
    """
    迁移 session_messages 到 Agno

    步骤：
    1. 为每个旧 session 生成 agno_session_id 并更新
    2. 将历史消息转换为 runs 数组格式
    3. 创建 agno_session 记录
    """
    logger.info("=" * 60)
    logger.info("开始迁移 session_messages -> Agno")
    logger.info("=" * 60)

    # 查询所有没有 agno_session_id 的 sessions
    sessions = db.query(SessionModel).filter(
        SessionModel.agno_session_id.is_(None)
    ).all()

    logger.info(f"找到 {len(sessions)} 个需要迁移的 sessions")

    if dry_run:
        logger.info("[DRY-RUN] 跳过实际迁移")
        for session in sessions:
            messages = db.query(SessionMessage).filter(
                SessionMessage.session_id == session.id
            ).count()
            logger.info(f"  Session {session.id}: {messages} 条消息")
        return 0, 0

    # 获取 TherapistAgent 的 agent_id
    therapist_service = TherapistAgentService()
    agent_id = therapist_service.agent.id

    migrated_sessions = 0
    migrated_messages = 0

    for session in sessions:
        # 生成 agno_session_id
        timestamp = int(session.start_time.timestamp())
        agno_session_id = f"session_{session.id}_{timestamp}"

        logger.info(f"\n处理 Session {session.id} -> {agno_session_id}")

        # 查询该 session 的所有消息
        messages = db.query(SessionMessage).filter(
            SessionMessage.session_id == session.id
        ).order_by(SessionMessage.created_at.asc()).all()

        logger.info(f"  找到 {len(messages)} 条消息")

        if len(messages) == 0:
            # 没有消息的 session，只更新 agno_session_id
            session.agno_session_id = agno_session_id
            db.commit()
            logger.info(f"  [SKIP] 空 session，仅更新 agno_session_id")
            migrated_sessions += 1
            continue

        try:
            # 更新 session 的 agno_session_id
            session.agno_session_id = agno_session_id

            # 将消息转换为 runs 数组
            # Agno 的 runs 格式：每个 run 包含一对用户输入和助手回复
            runs = []
            i = 0
            while i < len(messages):
                msg = messages[i]

                # 寻找配对的用户消息和助手回复
                if msg.sender == MessageSender.user:
                    user_input = msg.message
                    assistant_reply = None

                    # 查找下一条助手回复
                    if i + 1 < len(messages) and messages[i + 1].sender == MessageSender.therapist:
                        assistant_reply = messages[i + 1].message
                        i += 2
                    else:
                        # 没有回复，跳过这条消息
                        i += 1
                        continue

                    # 创建 run 对象
                    run = {
                        "input": {"input_content": user_input},
                        "model": "gpt-4o",
                        "run_id": f"migration_{session.id}_{len(runs)}",
                        "status": "COMPLETED",
                        "content": assistant_reply,
                        "created_at": int(msg.created_at.timestamp()) if msg.created_at else timestamp
                    }
                    runs.append(run)
                    migrated_messages += 2
                else:
                    # 跳过单独的助手消息
                    i += 1

            # 创建 agno_session 记录
            import json
            insert_query = text("""
                INSERT INTO ai.agno_sessions
                (session_id, session_type, agent_id, user_id, runs, created_at, updated_at)
                VALUES (:session_id, :session_type, :agent_id, :user_id, :runs, :created_at, :updated_at)
            """)

            db.execute(insert_query, {
                "session_id": agno_session_id,
                "session_type": "agent",
                "agent_id": agent_id,
                "user_id": str(session.user_id),
                "runs": json.dumps(runs),
                "created_at": timestamp,
                "updated_at": int(datetime.utcnow().timestamp())
            })

            db.commit()
            logger.info(f"  [OK] Session {session.id} 迁移完成（{len(runs)} 个 runs，{migrated_messages} 条消息）")
            migrated_sessions += 1

        except Exception as e:
            logger.error(f"  [ERROR] Session {session.id} 迁移失败: {e}")
            db.rollback()

    logger.info(f"\n迁移完成：{migrated_sessions} 个 sessions，{migrated_messages} 条消息")
    return migrated_sessions, migrated_messages


def main():
    parser = argparse.ArgumentParser(description="迁移数据到 Agno 框架")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览迁移，不实际执行"
    )
    parser.add_argument(
        "--skip-prompts",
        action="store_true",
        help="跳过 user_prompts 迁移"
    )
    parser.add_argument(
        "--skip-personas",
        action="store_true",
        help="跳过 user_personas 迁移"
    )
    parser.add_argument(
        "--skip-messages",
        action="store_true",
        help="跳过 session_messages 迁移"
    )

    args = parser.parse_args()

    if args.dry_run:
        logger.info("=" * 60)
        logger.info("预览模式（DRY-RUN）- 不会实际修改数据库")
        logger.info("=" * 60)

    # 获取数据库连接
    db = next(get_db())

    try:
        # 1. 迁移 user_prompts
        if not args.skip_prompts:
            migrate_user_prompts_to_contexts(db, dry_run=args.dry_run)

        # 2. 迁移 user_personas
        if not args.skip_personas:
            migrate_personas_to_memories(db, dry_run=args.dry_run)

        # 3. 迁移 session_messages
        if not args.skip_messages:
            migrate_session_messages_to_agno(db, dry_run=args.dry_run)

        logger.info("\n" + "=" * 60)
        logger.info("所有迁移任务完成！")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"迁移失败: {e}", exc_info=True)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
