from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ParticipantAnswerOption(Base):
    __tablename__ = "participant_answer_options"
    __table_args__ = (UniqueConstraint("participant_answer_id", "option_id"),)

    participant_answer_id: Mapped[int] = mapped_column(
        ForeignKey("participant_answers.id", ondelete="CASCADE"), nullable=False
    )
    option_id: Mapped[int] = mapped_column(ForeignKey("answer_options.id", ondelete="CASCADE"), nullable=False)