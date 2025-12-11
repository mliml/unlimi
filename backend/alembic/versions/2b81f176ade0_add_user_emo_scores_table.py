"""add_user_emo_scores_table

Revision ID: 2b81f176ade0
Revises: 8b1d32c5ea78
Create Date: 2025-12-09 13:59:43.050154

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b81f176ade0'
down_revision = '8b1d32c5ea78'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_emo_scores table
    # Note: Enum type will be created automatically by SQLAlchemy
    op.create_table(
        'user_emo_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stress_score', sa.Integer(), nullable=True),
        sa.Column('stable_score', sa.Integer(), nullable=True),
        sa.Column('anxiety_score', sa.Integer(), nullable=True),
        sa.Column('functional_score', sa.Integer(), nullable=True),
        sa.Column('stress_score_change', sa.Float(), nullable=True),
        sa.Column('stable_score_change', sa.Float(), nullable=True),
        sa.Column('anxiety_score_change', sa.Float(), nullable=True),
        sa.Column('functional_score_change', sa.Float(), nullable=True),
        sa.Column('source', sa.Enum('onboarding', 'session', name='emoscoresource', create_type=True), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_user_emo_scores_user_id', 'user_emo_scores', ['user_id'])
    op.create_index('ix_user_emo_scores_source', 'user_emo_scores', ['source'])
    op.create_index('ix_user_emo_scores_session_id', 'user_emo_scores', ['session_id'])
    op.create_index('ix_user_emo_scores_created_at', 'user_emo_scores', ['created_at'])
    op.create_index('ix_user_emo_scores_id', 'user_emo_scores', ['id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_user_emo_scores_id', table_name='user_emo_scores')
    op.drop_index('ix_user_emo_scores_created_at', table_name='user_emo_scores')
    op.drop_index('ix_user_emo_scores_session_id', table_name='user_emo_scores')
    op.drop_index('ix_user_emo_scores_source', table_name='user_emo_scores')
    op.drop_index('ix_user_emo_scores_user_id', table_name='user_emo_scores')

    # Drop table (Enum type will be dropped automatically by SQLAlchemy if not used elsewhere)
    op.drop_table('user_emo_scores')

    # Drop enum type manually
    sa.Enum(name='emoscoresource').drop(op.get_bind(), checkfirst=True)
