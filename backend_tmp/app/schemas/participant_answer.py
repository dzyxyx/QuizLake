from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AnswerSubmit(BaseModel):
    selected_option_ids: list[int]


class AnswerResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    question_id: int
    participant_id: int
    selected_option_ids: list[int]
    is_correct: bool
    response_time_ms: int | None = None
    points_awarded: int
    answered_at: datetime