"""drop unused quizzes.points_per_correct

Revision ID: a1b7c3d9e2f4
Revises: 6f2a9d4b8c31
Create Date: 2026-07-20 18:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b7c3d9e2f4'
down_revision: Union[str, Sequence[str], None] = '6f2a9d4b8c31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("quizzes", "points_per_correct")


def downgrade() -> None:
    op.add_column(
        "quizzes",
        sa.Column("points_per_correct", sa.SmallInteger(), nullable=False, server_default="100"),
    )
