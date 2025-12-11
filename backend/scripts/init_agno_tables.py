"""
Initialize Agno database tables

This script creates all necessary Agno framework tables in the database.
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# 设置临时 API key（仅用于初始化，不会实际调用 OpenAI API）
os.environ['OPENAI_API_KEY'] = 'sk-temp-for-init'

from app.agents.therapist_agent_service import TherapistAgentService
from app.agents.clerk_agent_service import ClerkAgentService
from sqlalchemy import inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_agno_tables():
    """
    初始化 Agno 表

    通过创建 Agent 服务并调用 _create_all_tables 方法
    """
    logger.info("=" * 60)
    logger.info("初始化 Agno 数据库表")
    logger.info("=" * 60)

    try:
        # 创建 TherapistAgent 服务
        logger.info("\n1. 初始化 TherapistAgentService...")
        therapist_service = TherapistAgentService()

        # 创建所有表
        logger.info("2. 创建 Agno 表...")
        therapist_service.agno_db._create_all_tables()

        # 验证表创建
        logger.info("\n3. 验证表创建...")
        inspector = inspect(therapist_service.agno_db.db_engine)
        tables = inspector.get_table_names()
        agno_tables = [t for t in tables if t.startswith('agno_')]

        if agno_tables:
            logger.info(f"✓ 成功创建 {len(agno_tables)} 个 Agno 表:")
            for table in agno_tables:
                logger.info(f"  - {table}")
        else:
            logger.warning("⚠ 未检测到 Agno 表，可能需要手动创建")

        logger.info("\n" + "=" * 60)
        logger.info("Agno 表初始化完成！")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"初始化失败: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = init_agno_tables()
    sys.exit(0 if success else 1)
