from pydantic import BaseModel, ConfigDict


class QuizCreate(BaseModel):
    category_id: int | None = None
    title: str
    description: str | None = None
    difficulty: str = "medium"
    time_per_question_sec: int = 15
    points_per_correct: int = 100
    speed_bonus_enabled: bool = False
    show_correct_answer: bool = True
    allow_answer_change: bool = False
    is_public: bool = False
    cover_image_url: str | None = None


class QuizRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    category_id: int | None = None
    title: str
    description: str | None = None
    difficulty: str
    time_per_question_sec: int
    points_per_correct: int
    speed_bonus_enabled: bool
    show_correct_answer: bool
    allow_answer_change: bool
    is_public: bool
    status: str
    cover_image_url: str | None = None


class QuizUpdate(BaseModel):
    category_id: int | None = None
    title: str | None = None
    description: str | None = None
    difficulty: str | None = None
    time_per_question_sec: int | None = None
    points_per_correct: int | None = None
    speed_bonus_enabled: bool | None = None
    show_correct_answer: bool | None = None
    allow_answer_change: bool | None = None
    is_public: bool | None = None
    status: str | None = None
    cover_image_url: str | None = None
