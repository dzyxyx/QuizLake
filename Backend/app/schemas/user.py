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