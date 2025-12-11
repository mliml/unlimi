"""add_user_context_and_agno_session_id

Revision ID: 8b1d32c5ea78
Revises: 2042da6b8ac9
Create Date: 2025-12-08 16:06:44.384856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b1d32c5ea78'
down_revision = '2042da6b8ac9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. 创建 user_contexts 表
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
    op.create_index('ix_user_contexts_user_id', 'user_contexts', ['user_id'])

    # 2. 添加 agno_session_id 到 sessions 表
    op.add_column('sessions', sa.Column('agno_session_id', sa.String(255), nullable=True))
    op.create_index('ix_sessions_agno_session_id', 'sessions', ['agno_session_id'])


def downgrade() -> None:
    # 删除 sessions 表的修改
    op.drop_index('ix_sessions_agno_session_id', 'sessions')
    op.drop_column('sessions', 'agno_session_id')

    # 删除 user_contexts 表
    op.drop_index('ix_user_contexts_user_id', 'user_contexts')
    op.drop_table('user_contexts')
