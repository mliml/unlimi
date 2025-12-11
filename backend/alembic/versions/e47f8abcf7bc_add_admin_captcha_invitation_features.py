"""add_admin_captcha_invitation_features

Revision ID: e47f8abcf7bc
Revises: 0103296fc90c
Create Date: 2025-12-11 21:47:11.815038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e47f8abcf7bc'
down_revision = '0103296fc90c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add is_admin column to users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))
    op.create_index('ix_users_is_admin', 'users', ['is_admin'])

    # 2. Create invitation_codes table
    op.create_table(
        'invitation_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('is_universal', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('used_by_user_id', sa.Integer(), nullable=True),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['used_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_invitation_codes_id', 'invitation_codes', ['id'])
    op.create_index('ix_invitation_codes_code', 'invitation_codes', ['code'], unique=True)
    op.create_index('ix_invitation_codes_is_used', 'invitation_codes', ['is_used'])

    # 3. Create captcha_sessions table
    op.create_table(
        'captcha_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('captcha_text', sa.String(length=4), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_captcha_sessions_id', 'captcha_sessions', ['id'])
    op.create_index('ix_captcha_sessions_session_id', 'captcha_sessions', ['session_id'], unique=True)

    # 4. Insert universal invitation code
    op.execute("""
        INSERT INTO invitation_codes (code, is_universal, is_used, created_at)
        VALUES ('WuSY_940315', true, false, now())
    """)


def downgrade() -> None:
    # Drop captcha_sessions table
    op.drop_index('ix_captcha_sessions_session_id', 'captcha_sessions')
    op.drop_index('ix_captcha_sessions_id', 'captcha_sessions')
    op.drop_table('captcha_sessions')

    # Drop invitation_codes table
    op.drop_index('ix_invitation_codes_is_used', 'invitation_codes')
    op.drop_index('ix_invitation_codes_code', 'invitation_codes')
    op.drop_index('ix_invitation_codes_id', 'invitation_codes')
    op.drop_table('invitation_codes')

    # Drop is_admin column from users table
    op.drop_index('ix_users_is_admin', 'users')
    op.drop_column('users', 'is_admin')
