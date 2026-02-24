"""Add OpenRouter provider support

Revision ID: add_openrouter_provider
Revises: add_anthropic_provider_fields
Create Date: 2026-02-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_openrouter_provider'
down_revision: Union[str, None] = 'add_anthropic_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add OpenRouter fields to users table
    op.add_column('users', sa.Column('openrouter_api_key', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('openrouter_model', sa.String(100), nullable=True, server_default='anthropic/claude-3.5-sonnet-20241022'))


def downgrade() -> None:
    # Remove OpenRouter fields from users table
    op.drop_column('users', 'openrouter_model')
    op.drop_column('users', 'openrouter_api_key')