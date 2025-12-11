"""add_session_messages_table

Revision ID: 9bd1a3def5f3
Revises: 8ad0f2ceb4e2
Create Date: 2025-12-05 23:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9bd1a3def5f3'
down_revision = '8ad0f2ceb4e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create session_messages table
    op.create_table('session_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('sender', sa.Enum('user', 'therapist', 'system', name='messagesender'), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_messages_session_id'), 'session_messages', ['session_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_session_messages_session_id'), table_name='session_messages')
    op.drop_table('session_messages')
    op.execute('DROP TYPE messagesender')
