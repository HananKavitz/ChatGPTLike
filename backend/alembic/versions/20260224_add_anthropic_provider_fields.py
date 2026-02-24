"""add_anthropic_provider_fields

Revision ID: add_anthropic_fields
Revises: 20260221_0935_initial_migration
Create Date: 2026-02-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_anthropic_fields'
down_revision = 'initial'
branch_labels = None
depends_on = None


def upgrade():
    # Add LLM provider fields to users table
    op.add_column('users', sa.Column('llm_provider', sa.String(20), nullable=False, server_default='openai'))
    op.add_column('users', sa.Column('anthropic_api_key', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('anthropic_model', sa.String(50), nullable=True, server_default='claude-opus-4-6'))


def downgrade():
    # Remove LLM provider fields from users table
    op.drop_column('users', 'anthropic_model')
    op.drop_column('users', 'anthropic_api_key')
    op.drop_column('users', 'llm_provider')