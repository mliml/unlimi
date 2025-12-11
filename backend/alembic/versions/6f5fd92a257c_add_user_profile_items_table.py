"""add_user_profile_items_table

Revision ID: 6f5fd92a257c
Revises: a3df599320a6
Create Date: 2025-12-07 00:15:04.329887

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f5fd92a257c'
down_revision = 'a3df599320a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user_profile_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Enum('low', 'medium', 'high', name='confidencelevel'), nullable=False),
        sa.Column('source', sa.Enum('onboarding', 'clerk', name='profilesource'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_profile_items_id'), 'user_profile_items', ['id'], unique=False)
    op.create_index(op.f('ix_user_profile_items_user_id'), 'user_profile_items', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_profile_items_user_id'), table_name='user_profile_items')
    op.drop_index(op.f('ix_user_profile_items_id'), table_name='user_profile_items')
    op.drop_table('user_profile_items')
