"""seed default categories

Revision ID: 6f2a9d4b8c31
Revises: 457b080a57e1
Create Date: 2026-07-20 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '6f2a9d4b8c31'
down_revision: Union[str, Sequence[str], None] = '457b080a57e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

categories_table = sa.table(
    "categories",
    sa.column("name", sa.String),
    sa.column("slug", sa.String),
    sa.column("icon", sa.String),
)

CATEGORIES = [
    {"name": "История", "slug": "istoriya", "icon": "📜"},
    {"name": "География", "slug": "geografiya", "icon": "🌍"},
    {"name": "Наука", "slug": "nauka", "icon": "🔬"},
    {"name": "Кино и сериалы", "slug": "kino-i-serialy", "icon": "🎬"},
    {"name": "Музыка", "slug": "muzyka", "icon": "🎵"},
    {"name": "Спорт", "slug": "sport", "icon": "⚽"},
    {"name": "Литература", "slug": "literatura", "icon": "📚"},
]


def upgrade() -> None:
    op.bulk_insert(categories_table, CATEGORIES)


def downgrade() -> None:
    conn = op.get_bind()
    slugs = [c["slug"] for c in CATEGORIES]
    conn.execute(
        sa.text("DELETE FROM categories WHERE slug = ANY(:slugs)"),
        {"slugs": slugs},
    )
