"""drop_system_prompts_table

Revision ID: 2042da6b8ac9
Revises: 6f5fd92a257c
Create Date: 2025-12-07 15:08:59.481191

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2042da6b8ac9'
down_revision = '6f5fd92a257c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 检查表是否存在
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if 'system_prompts' in tables:
        # 删除索引（如果存在）
        indexes = [idx['name'] for idx in inspector.get_indexes('system_prompts')]
        if 'ix_system_prompts_name' in indexes:
            op.drop_index(op.f('ix_system_prompts_name'), table_name='system_prompts')
        if 'ix_system_prompts_id' in indexes:
            op.drop_index(op.f('ix_system_prompts_id'), table_name='system_prompts')
        # 删除表
        op.drop_table('system_prompts')


def downgrade() -> None:
    # 重新创建表（如果需要回滚）
    op.create_table('system_prompts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_prompts_id'), 'system_prompts', ['id'], unique=False)
    op.create_index(op.f('ix_system_prompts_name'), 'system_prompts', ['name'], unique=True)
