from fastapi import APIRouter, Depends, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import Question, User, AnswerOption
from app.schemas.question import QuestionCreate, QuestionRead, QuestionUpdate
from app.api.deps import get_current_user, get_owned_quiz_or_403, get_question_or_404


router = APIRouter()


@router.post("", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question(
    quiz_id: int,
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await get_owned_quiz_or_403(quiz_id, current_user, db)

    question_dict = question_data.model_dump(exclude={"answer_options"})
    new_question = Question(**question_dict, quiz_id=quiz_id)
    db.add(new_question)
    await db.flush()

    for option_data in question_data.answer_options:
        db.add(AnswerOption(**option_data.model_dump(), question_id=new_question.id))

    await db.commit()
    await db.refresh(new_question)
    return new_question


@router.get("", response_model=list[QuestionRead])
async def get_questions(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await get_owned_quiz_or_403(quiz_id, current_user, db)

    query = select(Question).where(Question.quiz_id == quiz_id).order_by(Question.order_index)
    result = await db.execute(query)

    questions = result.scalars().all()
    return questions


@router.patch("/{question_id}", response_model=QuestionRead)
async def update_question(
    quiz_id: int,
    question_id: int,
    question_data: QuestionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    question = await get_question_or_404(quiz_id, question_id, current_user, db)

    update_data = question_data.model_dump(exclude_unset=True, exclude={"answer_options"})
    for field, value in update_data.items():
        setattr(question, field, value)

    if question_data.answer_options is not None:
        for option in list(question.answer_options):
            await db.delete(option)
        await db.flush()
        for option_data in question_data.answer_options:
            db.add(AnswerOption(**option_data.model_dump(), question_id=question.id))

    await db.commit()
    await db.refresh(question)

    return question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    quiz_id: int,
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    question = await get_question_or_404(quiz_id, question_id, current_user, db)

    await db.delete(question)
    await db.commit()