"""Add submit_message column to forms table

Revision ID: 0003_add_submit_message
Revises: 0002_add_auth_tables
Create Date: 2026-07-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003_add_submit_message'
down_revision: Union[str, Sequence[str], None] = '0002_add_auth_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the per-form submit confirmation message."""
    op.add_column('forms', sa.Column('submit_message', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('forms', 'submit_message')
