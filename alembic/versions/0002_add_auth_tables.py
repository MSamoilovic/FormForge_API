"""Add authentication tables (users, organizations, api_keys)

Revision ID: 0002_add_auth_tables
Revises: f94b2d03aa3b
Create Date: 2026-01-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002_add_auth_tables'
down_revision: Union[str, None] = 'f94b2d03aa3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create userrole enum type
    userrole_enum = sa.Enum(
        'super_admin', 'org_admin', 'form_creator', 'viewer',
        name='userrole'
    )
    userrole_enum.create(op.get_bind(), checkfirst=True)
    
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('plan', sa.String(), nullable=True, server_default='free'),
        sa.Column('max_forms', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('max_submissions_per_month', sa.Integer(), nullable=True, server_default='1000'),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('role', userrole_enum, nullable=True, server_default='form_creator'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('scopes', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_keys_id'), 'api_keys', ['id'], unique=False)
    op.create_index(op.f('ix_api_keys_key'), 'api_keys', ['key'], unique=True)
    
    # Add owner_id and organization_id columns to forms table
    op.add_column('forms', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.add_column('forms', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('forms', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('forms', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Add foreign keys to forms
    op.create_foreign_key(
        'fk_forms_owner_id', 
        'forms', 'users', 
        ['owner_id'], ['id']
    )
    op.create_foreign_key(
        'fk_forms_organization_id', 
        'forms', 'organizations', 
        ['organization_id'], ['id']
    )


def downgrade() -> None:
    # Remove foreign keys from forms
    op.drop_constraint('fk_forms_organization_id', 'forms', type_='foreignkey')
    op.drop_constraint('fk_forms_owner_id', 'forms', type_='foreignkey')
    
    # Remove columns from forms
    op.drop_column('forms', 'updated_at')
    op.drop_column('forms', 'created_at')
    op.drop_column('forms', 'organization_id')
    op.drop_column('forms', 'owner_id')
    
    # Drop api_keys table
    op.drop_index(op.f('ix_api_keys_key'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_id'), table_name='api_keys')
    op.drop_table('api_keys')
    
    # Drop users table
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Drop organizations table
    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    op.drop_table('organizations')
    
    # Drop enum type
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)

