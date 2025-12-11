"""fix_onboarding_answer_nullable

Revision ID: 365abef65d36
Revises: a1b2c3d4e5f6
Create Date: 2025-12-09 22:41:43.663305

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '365abef65d36'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make answer column nullable (allow NULL for unanswered questions)
    op.alter_column('user_onboardings', 'answer',
                    existing_type=sa.Text(),
                    nullable=True)


def downgrade() -> None:
    # Revert: make answer column NOT NULL
    # Note: This might fail if there are NULL values in the column
    op.alter_column('user_onboardings', 'answer',
                    existing_type=sa.Text(),
                    nullable=False)
