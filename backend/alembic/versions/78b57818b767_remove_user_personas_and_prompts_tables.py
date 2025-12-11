"""remove_user_personas_and_prompts_tables

Revision ID: 78b57818b767
Revises: 365abef65d36
Create Date: 2025-12-10 23:39:10.660618

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78b57818b767'
down_revision = '365abef65d36'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 删除 user_personas 表
    op.drop_table('user_personas')

    # 删除 user_prompts 表
    op.drop_table('user_prompts')


def downgrade() -> None:
    # 回滚：重新创建 user_prompts 表
    op.create_table(
        'user_prompts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('counselor', name='prompttype'), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'type', name='uq_user_prompt_type')
    )
    op.create_index(op.f('ix_user_prompts_user_id'), 'user_prompts', ['user_id'], unique=False)

    # 回滚：重新创建 user_personas 表
    op.create_table(
        'user_personas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Enum('low', 'medium', 'high', name='confidencelevel'), nullable=False),
        sa.Column('source', sa.Enum('onboarding', 'clerk', name='profilesource'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_user_personas_user_id'), 'user_personas', ['user_id'], unique=False)
