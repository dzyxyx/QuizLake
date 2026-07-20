from pydantic import BaseModel, ConfigDict
from app.schemas.answer_option import AnswerOptionCreate, AnswerOptionRead


class QuestionCreate(BaseModel):
    question_text: str
    image_url: str | None = None
    question_type: str = "single"
    order_index: int
    time_limit_sec: int | None = None
    points: int | None = None
    answer_options: list[AnswerOptionCreate]


class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_text: str
    image_url: str | None = None
    question_type: str
    order_index: int
    time_limit_sec: int | None = None
    points: int | None = None
    answer_options: list[AnswerOptionRead]


class QuestionUpdate(BaseModel):
    question_text: str | None = None
    image_url: str | None = None
    question_type: str | None = None
    order_index: int | None = None
    time_limit_sec: int | None = None
    points: int | None = None
    answer_options: list[AnswerOptionCreate] | None = None