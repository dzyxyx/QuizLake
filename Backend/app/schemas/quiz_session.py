from pydantic import BaseModel, ConfigDict
from datetime import datetime


class QuizSessionCreate(BaseModel):
    scheduled_start_at: datetime | None = None


class QuizSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int
    host_id: int
    room_code: str
    status: str
    current_question_id: int | None = None
    current_question_started_at: datetime | None = None
    scheduled_start_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
