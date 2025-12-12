"""initial complete schema

Revision ID: 001
Revises:
Create Date: 2025-12-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create therapists table
    op.create_table('therapists',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('intro', sa.Text(), nullable=False),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_therapists_id'), 'therapists', ['id'], unique=False)

    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('nickname', sa.String(), nullable=True),
        sa.Column('therapist_id', sa.String(), nullable=False, server_default='01'),
        sa.Column('has_finished_onboarding', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['therapist_id'], ['therapists.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_is_admin'), 'users', ['is_admin'], unique=False)

    # Create user_onboardings table
    # The questiontype enum will be created automatically by SQLAlchemy
    op.create_table('user_onboardings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_number', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', postgresql.ENUM('choice', 'text', name='questiontype'), nullable=False),
        sa.Column('question_options', sa.JSON(), nullable=True),
        sa.Column('answer', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('answered_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_onboardings_id'), 'user_onboardings', ['id'], unique=False)
    op.create_index(op.f('ix_user_onboardings_user_id'), 'user_onboardings', ['user_id'], unique=False)
    op.create_index('ix_user_onboardings_user_question', 'user_onboardings', ['user_id', 'question_number'])

    # Create user_context table
    op.create_table('user_context',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('agno_session_id', sa.String(), nullable=True),
        sa.Column('context_summary', sa.Text(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_context_id'), 'user_context', ['id'], unique=False)
    op.create_index(op.f('ix_user_context_user_id'), 'user_context', ['user_id'], unique=True)

    # Create sessions table
    op.create_table('sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('therapist_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('mood_before', sa.Integer(), nullable=True),
        sa.Column('mood_after', sa.Integer(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('key_events', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['therapist_id'], ['therapists.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sessions_id'), 'sessions', ['id'], unique=False)
    op.create_index(op.f('ix_sessions_user_id'), 'sessions', ['user_id'], unique=False)

    # Create session_plans table
    op.create_table('session_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('plan_content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_plans_id'), 'session_plans', ['id'], unique=False)
    op.create_index(op.f('ix_session_plans_session_id'), 'session_plans', ['session_id'], unique=True)

    # Create session_messages table
    op.create_table('session_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_messages_id'), 'session_messages', ['id'], unique=False)
    op.create_index(op.f('ix_session_messages_session_id'), 'session_messages', ['session_id'], unique=False)

    # Create session_reviews table
    op.create_table('session_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('review_content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_reviews_id'), 'session_reviews', ['id'], unique=False)
    op.create_index(op.f('ix_session_reviews_session_id'), 'session_reviews', ['session_id'], unique=True)

    # Create user_emo_scores table
    op.create_table('user_emo_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('emo_score_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_emo_scores_id'), 'user_emo_scores', ['id'], unique=False)
    op.create_index(op.f('ix_user_emo_scores_user_id'), 'user_emo_scores', ['user_id'], unique=False)

    # Create captcha_sessions table
    op.create_table('captcha_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('captcha_text', sa.String(length=4), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_captcha_sessions_id'), 'captcha_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_captcha_sessions_session_id'), 'captcha_sessions', ['session_id'], unique=True)

    # Create invitation_codes table
    op.create_table('invitation_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('used_by_email', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invitation_codes_code'), 'invitation_codes', ['code'], unique=True)
    op.create_index(op.f('ix_invitation_codes_id'), 'invitation_codes', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_invitation_codes_id'), table_name='invitation_codes')
    op.drop_index(op.f('ix_invitation_codes_code'), table_name='invitation_codes')
    op.drop_table('invitation_codes')

    op.drop_index(op.f('ix_captcha_sessions_session_id'), table_name='captcha_sessions')
    op.drop_index(op.f('ix_captcha_sessions_id'), table_name='captcha_sessions')
    op.drop_table('captcha_sessions')

    op.drop_index(op.f('ix_user_emo_scores_user_id'), table_name='user_emo_scores')
    op.drop_index(op.f('ix_user_emo_scores_id'), table_name='user_emo_scores')
    op.drop_table('user_emo_scores')

    op.drop_index(op.f('ix_session_reviews_session_id'), table_name='session_reviews')
    op.drop_index(op.f('ix_session_reviews_id'), table_name='session_reviews')
    op.drop_table('session_reviews')

    op.drop_index(op.f('ix_session_messages_session_id'), table_name='session_messages')
    op.drop_index(op.f('ix_session_messages_id'), table_name='session_messages')
    op.drop_table('session_messages')

    op.drop_index(op.f('ix_session_plans_session_id'), table_name='session_plans')
    op.drop_index(op.f('ix_session_plans_id'), table_name='session_plans')
    op.drop_table('session_plans')

    op.drop_index(op.f('ix_sessions_user_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_id'), table_name='sessions')
    op.drop_table('sessions')

    op.drop_index(op.f('ix_user_context_user_id'), table_name='user_context')
    op.drop_index(op.f('ix_user_context_id'), table_name='user_context')
    op.drop_table('user_context')

    op.drop_index('ix_user_onboardings_user_question', table_name='user_onboardings')
    op.drop_index(op.f('ix_user_onboardings_user_id'), table_name='user_onboardings')
    op.drop_index(op.f('ix_user_onboardings_id'), table_name='user_onboardings')
    op.drop_table('user_onboardings')

    postgresql.ENUM(name='questiontype').drop(op.get_bind(), checkfirst=True)

    op.drop_index(op.f('ix_users_is_admin'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_therapists_id'), table_name='therapists')
    op.drop_table('therapists')
