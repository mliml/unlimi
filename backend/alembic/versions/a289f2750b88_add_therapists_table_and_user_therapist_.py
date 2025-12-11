"""add_therapists_table_and_user_therapist_id

Revision ID: a289f2750b88
Revises: 78b57818b767
Create Date: 2025-12-11 00:19:59.576423

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a289f2750b88'
down_revision = '78b57818b767'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Create therapists table
    op.create_table(
        'therapists',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('info', sa.Text(), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_therapists_id'), 'therapists', ['id'], unique=False)

    # Step 2: Insert initial therapist data
    op.execute("""
        INSERT INTO therapists (id, name, age, info, prompt) VALUES
        ('01', 'Dora', 35, '35岁女性咨询师，精神分析流派', ''),
        ('02', 'Jakkie', 38, '38岁男性咨询师，人本主义+格式塔流派', '')
    """)

    # Step 3: Add therapist_id column to users table
    op.add_column('users', sa.Column('therapist_id', sa.String(), nullable=False, server_default='01'))
    op.create_foreign_key('fk_users_therapist_id', 'users', 'therapists', ['therapist_id'], ['id'])


def downgrade() -> None:
    # Remove foreign key and column from users table
    op.drop_constraint('fk_users_therapist_id', 'users', type_='foreignkey')
    op.drop_column('users', 'therapist_id')

    # Drop therapists table
    op.drop_index(op.f('ix_therapists_id'), table_name='therapists')
    op.drop_table('therapists')
