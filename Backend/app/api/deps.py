from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import Quiz, Question, QuizSession
from app.db.models.user import User
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def _get_user_from_token(token: str | None, db: AsyncSession) -> User | None:
    if token is None:
        return None

    try:
        payload = decode_access_token(token)
    except JWTError:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    result = await db.execute(select(User).where(User.id == int(user_id)))
    return result.scalar_one_or_none()


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    user = await _get_user_from_token(token, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не удалось подтвердить учётные данные")
    return user


async def get_current_user_optional(
token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User | None:
    return await _get_user_from_token(token, db)


async def get_quiz_or_404(quiz_id: int, db: AsyncSession) -> Quiz:
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Квиз не найден")
    return quiz


async def get_owned_quiz_or_403(quiz_id: int, current_user: User, db: AsyncSession) -> Quiz:
    quiz = await get_quiz_or_404(quiz_id, db)
    if quiz.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")
    return quiz


async def get_question_or_404(
    quiz_id: int, question_id: int, current_user: User, db: AsyncSession
) -> Question:
    await get_owned_quiz_or_403(quiz_id, current_user, db)

    result = await db.execute(
        select(Question).where(Question.id == question_id, Question.quiz_id == quiz_id)
    )
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден")
    return question


async def get_session_by_code_or_404(
        room_code: str,
        db: AsyncSession,
) -> QuizSession:
    result = await db.execute(select(QuizSession).where(QuizSession.room_code == room_code))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комната не найдена")
    return session


async def get_session_or_404(session_id: int, db: AsyncSession) -> QuizSession:
    result = await db.execute(select(QuizSession).where(QuizSession.id == session_id))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сессия не найдена")
    return session