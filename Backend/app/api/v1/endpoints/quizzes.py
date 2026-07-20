from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import Quiz, User
from app.schemas.quiz import QuizCreate, QuizRead, QuizUpdate
from app.api.deps import get_current_user, get_current_user_optional, get_quiz_or_404, get_owned_quiz_or_403


router = APIRouter()


@router.post("", response_model=QuizRead, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    quiz_data: QuizCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ):
    new_quiz = Quiz(**quiz_data.model_dump(), owner_id=current_user.id)
    
    db.add(new_quiz)
    await db.commit()
    await db.refresh(new_quiz)
    
    return new_quiz


@router.get("", response_model=list[QuizRead])
async def get_quizzes(
    status: str | None = None, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Quiz).where(Quiz.owner_id == current_user.id)

    if status is not None:
        query = query.where(Quiz.status == status)
    
    result = await db.execute(query)
    quizzes = result.scalars().all()

    return quizzes


@router.get("/{quiz_id}", response_model=QuizRead)
async def get_quiz(
    quiz_id: int,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    quiz = await get_quiz_or_404(quiz_id, db)

    is_owner = current_user is not None and quiz.owner_id == current_user.id
    is_public_ready = quiz.status == "ready" and quiz.is_public

    if not is_owner and not is_public_ready:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")
    
    return quiz


@router.patch("/{quiz_id}", response_model=QuizRead)
async def update_quiz(
    quiz_id: int,
    quiz_data: QuizUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    quiz = await get_owned_quiz_or_403(quiz_id, current_user, db)

    update_data = quiz_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(quiz, field, value)

    await db.commit()
    await db.refresh(quiz)

    return quiz


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    quiz = await get_owned_quiz_or_403(quiz_id, current_user, db)

    await db.delete(quiz)
    await db.commit()