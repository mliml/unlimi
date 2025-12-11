"""update_onboarding_schema

Revision ID: a1b2c3d4e5f6
Revises: 2b81f176ade0
Create Date: 2025-12-09 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '2b81f176ade0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add nickname column to users table
    op.add_column('users', sa.Column('nickname', sa.String(), nullable=True))

    # 2. Create Enum type first (for PostgreSQL)
    questiontype_enum = postgresql.ENUM('choice', 'text', name='questiontype', create_type=False)
    questiontype_enum.create(op.get_bind(), checkfirst=True)

    # 3. Add new columns to user_onboardings table
    op.add_column('user_onboardings', sa.Column('question_number', sa.Integer(), nullable=True))
    op.add_column('user_onboardings', sa.Column('question_type',
                  sa.Enum('choice', 'text', name='questiontype', create_type=False), nullable=True))
    op.add_column('user_onboardings', sa.Column('question_options', sa.JSON(), nullable=True))
    op.add_column('user_onboardings', sa.Column('answered_at', sa.DateTime(), nullable=True))

    # 3. Migrate existing data (if any)
    # Rename 'question' column to 'question_text' if it exists
    # For existing records, set question_type='text' and question_number based on created_at order

    # Note: This migration assumes the old schema had a 'question' column
    # If the current table is empty or has different structure, adjust accordingly

    # Check if we need to migrate data from 'question' column
    # We'll use execute with raw SQL for this
    connection = op.get_bind()

    # Check if 'question' column exists
    result = connection.execute(sa.text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='user_onboardings' AND column_name='question'
    """))

    if result.fetchone():
        # Rename 'question' to 'question_text'
        op.alter_column('user_onboardings', 'question', new_column_name='question_text')

        # Set default values for new columns in existing records
        # Use CTE to calculate row numbers first, then update
        connection.execute(sa.text("""
            WITH numbered_rows AS (
                SELECT id, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) as row_num
                FROM user_onboardings
            )
            UPDATE user_onboardings
            SET question_type = 'text',
                question_number = numbered_rows.row_num
            FROM numbered_rows
            WHERE user_onboardings.id = numbered_rows.id
                AND user_onboardings.question_type IS NULL
        """))
    else:
        # No old data to migrate, just add the question_text column
        op.add_column('user_onboardings', sa.Column('question_text', sa.Text(), nullable=True))

    # 4. Make question_number and question_type NOT NULL after migration
    op.alter_column('user_onboardings', 'question_number', nullable=False)
    op.alter_column('user_onboardings', 'question_type', nullable=False)
    op.alter_column('user_onboardings', 'question_text', nullable=False)

    # 5. Create index on user_id and question_number
    op.create_index('ix_user_onboardings_user_question', 'user_onboardings',
                    ['user_id', 'question_number'])


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_user_onboardings_user_question', table_name='user_onboardings')

    # Remove columns from user_onboardings
    op.drop_column('user_onboardings', 'answered_at')
    op.drop_column('user_onboardings', 'question_options')
    op.drop_column('user_onboardings', 'question_type')
    op.drop_column('user_onboardings', 'question_number')

    # Rename question_text back to question
    op.alter_column('user_onboardings', 'question_text', new_column_name='question')

    # Remove nickname from users
    op.drop_column('users', 'nickname')

    # Drop enum type
    sa.Enum(name='questiontype').drop(op.get_bind(), checkfirst=True)
