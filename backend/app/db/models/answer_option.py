from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, SmallInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.question import Question


class AnswerOption(Base):
    __tablename__ = "answer_options"

    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    option_text: Mapped[str] = mapped_column(String(500), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    question: Mapped["Question"] = relationship(back_populates="answer_options")