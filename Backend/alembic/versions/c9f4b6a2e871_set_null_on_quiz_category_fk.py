"""set ON DELETE SET NULL on quizzes.category_id fk

Revision ID: c9f4b6a2e871
Revises: d4e8f1a29b6c
Create Date: 2026-07-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c9f4b6a2e871'
down_revision: Union[str, Sequence[str], None] = 'd4e8f1a29b6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('quizzes_category_id_fkey', 'quizzes', type_='foreignkey')
    op.create_foreign_key(
        'quizzes_category_id_fkey', 'quizzes', 'categories', ['category_id'], ['id'], ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('quizzes_category_id_fkey', 'quizzes', type_='foreignkey')
    op.create_foreign_key('quizzes_category_id_fkey', 'quizzes', 'categories', ['category_id'], ['id'])
