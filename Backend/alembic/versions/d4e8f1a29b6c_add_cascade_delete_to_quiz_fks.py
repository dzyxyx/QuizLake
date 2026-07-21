"""add ON DELETE CASCADE to quiz/session foreign keys

Revision ID: d4e8f1a29b6c
Revises: a1b7c3d9e2f4
Create Date: 2026-07-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd4e8f1a29b6c'
down_revision: Union[str, Sequence[str], None] = 'a1b7c3d9e2f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CASCADES = [
    ('questions_quiz_id_fkey', 'questions', 'quizzes', 'quiz_id', 'id', 'CASCADE'),
    ('answer_options_question_id_fkey', 'answer_options', 'questions', 'question_id', 'id', 'CASCADE'),
    ('quiz_sessions_quiz_id_fkey', 'quiz_sessions', 'quizzes', 'quiz_id', 'id', 'CASCADE'),
    ('quiz_sessions_current_question_id_fkey', 'quiz_sessions', 'questions', 'current_question_id', 'id', 'SET NULL'),
    ('session_participants_session_id_fkey', 'session_participants', 'quiz_sessions', 'session_id', 'id', 'CASCADE'),
    ('session_reminders_session_id_fkey', 'session_reminders', 'quiz_sessions', 'session_id', 'id', 'CASCADE'),
    ('participant_answers_session_id_fkey', 'participant_answers', 'quiz_sessions', 'session_id', 'id', 'CASCADE'),
    ('participant_answers_question_id_fkey', 'participant_answers', 'questions', 'question_id', 'id', 'CASCADE'),
    (
        'participant_answers_participant_id_fkey',
        'participant_answers',
        'session_participants',
        'participant_id',
        'id',
        'CASCADE',
    ),
    (
        'participant_answer_options_participant_answer_id_fkey',
        'participant_answer_options',
        'participant_answers',
        'participant_answer_id',
        'id',
        'CASCADE',
    ),
    (
        'participant_answer_options_option_id_fkey',
        'participant_answer_options',
        'answer_options',
        'option_id',
        'id',
        'CASCADE',
    ),
]


def upgrade() -> None:
    """Upgrade schema."""
    for name, table, ref_table, col, ref_col, ondelete in CASCADES:
        op.drop_constraint(name, table, type_='foreignkey')
        op.create_foreign_key(name, table, ref_table, [col], [ref_col], ondelete=ondelete)


def downgrade() -> None:
    """Downgrade schema."""
    for name, table, ref_table, col, ref_col, _ in CASCADES:
        op.drop_constraint(name, table, type_='foreignkey')
        op.create_foreign_key(name, table, ref_table, [col], [ref_col])
