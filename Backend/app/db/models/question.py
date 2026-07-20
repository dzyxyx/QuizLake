from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String, SmallInteger, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import CreatedAtMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from app.db.models.answer_option import AnswerOption


class QuestionType(str, Enum):
    SINGLE = 'single'
    MULTIPLE = 'multiple'


class Question(Base, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "questions"
    __table_args__ = (UniqueConstraint("quiz_id", "order_index"),)

    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))
    question_type: Mapped[str] = mapped_column(String(20), default=QuestionType.SINGLE)
    order_index: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    time_limit_sec: Mapped[int | None] = mapped_column(SmallInteger)
    points: Mapped[int | None] = mapped_column(SmallInteger)
    answer_options: Mapped[list["AnswerOption"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )
