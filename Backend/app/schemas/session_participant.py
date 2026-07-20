from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ParticipantJoin(BaseModel):
    display_name: str
    avatar_url: str | None = None


class ParticipantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    user_id: int | None = None
    display_name: str
    avatar_url: str | None = None
    total_score: int
    correct_answers_count: int
    final_rank: int | None = None
    is_connected: bool
    joined_at: datetime
    left_at: datetime | None = None