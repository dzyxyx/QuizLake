"""add server default to session_participants.joined_at

Revision ID: 457b080a57e1
Revises: a3f8fed36fc1
Create Date: 2026-07-20 16:42:52.270500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '457b080a57e1'
down_revision: Union[str, Sequence[str], None] = 'a3f8fed36fc1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "session_participants",
        "joined_at",
        server_default=sa.text("now()"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "session_participants",
        "joined_at",
        server_default=None,
    )
