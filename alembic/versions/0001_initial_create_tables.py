"""Initial migration - create base tables

Revision ID: 0001_initial
Revises: 
Create Date: 2025-12-24 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create forms table
    op.create_table(
        'forms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('fields', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('rules', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forms_id'), 'forms', ['id'], unique=False)
    op.create_index(op.f('ix_forms_name'), 'forms', ['name'], unique=False)

    # Create submissions table
    op.create_table(
        'submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('form_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['form_id'], ['forms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submissions_id'), 'submissions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_submissions_id'), table_name='submissions')
    op.drop_table('submissions')
    op.drop_index(op.f('ix_forms_name'), table_name='forms')
    op.drop_index(op.f('ix_forms_id'), table_name='forms')
    op.drop_table('forms')

