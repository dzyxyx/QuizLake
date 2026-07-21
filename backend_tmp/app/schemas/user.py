from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    nickname: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    nickname: str
    email: EmailStr
    avatar_url: str | None = None


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    nickname: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    avatar_url: str | None = None


class UserStats(BaseModel):
    played: int
    wins: int
    created: int
    hosted_sessions_count: int
    avg_score_percent: int


class ParticipationHistoryItem(BaseModel):
    session_id: int
    room_code: str
    quiz_title: str
    ended_at: datetime | None = None
    participants_count: int
    final_rank: int | None = None


class HostedSessionHistoryItem(BaseModel):
    session_id: int
    room_code: str
    quiz_title: str
    ended_at: datetime | None = None
    participants_count: int