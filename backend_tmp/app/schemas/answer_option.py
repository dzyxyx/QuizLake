from pydantic import BaseModel, ConfigDict


class AnswerOptionCreate(BaseModel):
    option_text: str
    is_correct: bool = False
    order_index: int


class AnswerOptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    option_text: str
    is_correct: bool
    order_index: int