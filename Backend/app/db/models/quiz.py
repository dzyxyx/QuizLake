from enum import Enum

from sqlalchemy import String, ForeignKey, Boolean, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import CreatedAtMixin, UpdatedAtMixin


class Difficulty(str, Enum):
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'


class QuizStatus(str, Enum):
    DRAFT = 'draft'
    READY = 'ready'
    ARCHIVED = 'archived'


class Quiz(Base, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "quizzes"

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int| None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(String(50), default=Difficulty.MEDIUM)
    time_per_question_sec: Mapped[int] = mapped_column(SmallInteger, default=15)
    points_per_correct: Mapped[int] = mapped_column(SmallInteger, default=100)
    speed_bonus_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    show_correct_answer: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_answer_change: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(50), default=QuizStatus.DRAFT)
    cover_image_url: Mapped[str | None] = mapped_column(String(500))