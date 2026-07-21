from datetime import datetime

from sqlalchemy import ForeignKey, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import CreatedAtMixin


class SessionReminder(Base, CreatedAtMixin):
    __tablename__ = "session_reminders"
    __table_args__ = (UniqueConstraint("session_id", "user_id"),)

    session_id: Mapped[int] = mapped_column(ForeignKey("quiz_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notified: Mapped[bool] = mapped_column(Boolean, default=False)