from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Boolean, SmallInteger, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ParticipantAnswer(Base):
    __tablename__ = "participant_answers"
    __table_args__ = (UniqueConstraint("participant_id", "question_id"),)

    session_id: Mapped[int] = mapped_column(ForeignKey("quiz_sessions.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    participant_id: Mapped[int] = mapped_column(ForeignKey("session_participants.id"), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    points_awarded: Mapped[int] = mapped_column(SmallInteger, default=0)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )