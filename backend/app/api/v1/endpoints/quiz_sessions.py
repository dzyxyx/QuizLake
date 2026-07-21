from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, status

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.websockets.manager import manager

from app.db.session import get_db
from app.db.models import QuizSession, User, SessionParticipant, Question
from app.schemas.quiz_session import QuizSessionCreate, QuizSessionRead
from app.schemas.question import QuestionRead
from app.schemas.session_participant import ParticipantRead, ParticipantJoin
from app.api.deps import get_owned_quiz_or_403, get_current_user, get_current_user_optional, get_session_by_code_or_404, get_session_or_404
from app.core.security import generate_room_code


router = APIRouter()
public_router = APIRouter()


@router.post("", response_model=QuizSessionRead, status_code=status.HTTP_201_CREATED)
async def create_session(
    quiz_id: int,
    session_data: QuizSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    quiz = await get_owned_quiz_or_403(quiz_id, current_user, db)

    if quiz.status != "ready":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Квиз не готов к запуску")

    if session_data.scheduled_start_at is not None:
        scheduled = session_data.scheduled_start_at
        if scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=timezone.utc)
        if scheduled <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Время старта должно быть в будущем",
            )

    while True:
        code = generate_room_code()
        result = await db.execute(select(QuizSession).where(QuizSession.room_code == code))
        if result.scalar_one_or_none() is None:
            break
    
    new_session = QuizSession(
        quiz_id=quiz_id,
        host_id=current_user.id,
        room_code=code,
        scheduled_start_at=session_data.scheduled_start_at,
    )
    
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return new_session


@public_router.get("/{room_code}", response_model=QuizSessionRead)
async def get_session_by_code(room_code: str, db: AsyncSession = Depends(get_db)):

    return  await get_session_by_code_or_404(room_code, db)


@public_router.post("/{room_code}/join", response_model=ParticipantRead, status_code=status.HTTP_201_CREATED)
async def join_session(
    room_code: str,
    join_data: ParticipantJoin,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    session = await get_session_by_code_or_404(room_code, db)
    if session.status != "waiting":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя присоединиться к уже начавшейся или завершённой игре")

    user_id = current_user.id if current_user else None

    if current_user is not None and session.host_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы организатор этой игры — присоединиться как участник нельзя",
        )

    if current_user is not None:
        existing = await db.execute(
            select(SessionParticipant).where(
                SessionParticipant.session_id == session.id,
                SessionParticipant.user_id == current_user.id,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Вы уже в этой комнате")

    display_name = join_data.display_name.strip()

    existing_name = await db.execute(
        select(SessionParticipant).where(
            SessionParticipant.session_id == session.id,
            func.lower(SessionParticipant.display_name) == display_name.lower(),
        )
    )
    if existing_name.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой ник уже занят в этой комнате — выберите другой",
        )

    new_participant = SessionParticipant(
        session_id=session.id,
        user_id=user_id,
        display_name=display_name,
        avatar_url=join_data.avatar_url,
    )

    db.add(new_participant)
    await db.commit()
    await db.refresh(new_participant)

    await manager.broadcast(session.id, {
        "type": "participant_joined",
        "payload": ParticipantRead.model_validate(new_participant).model_dump(mode="json")
    })

    return new_participant


@public_router.delete("/{session_id}/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def leave_session(session_id: int, participant_id: int, db: AsyncSession = Depends(get_db)):
    session = await get_session_or_404(session_id, db)
    if session.status != "waiting":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя покинуть комнату — игра уже началась",
        )

    result = await db.execute(
        select(SessionParticipant).where(
            SessionParticipant.id == participant_id,
            SessionParticipant.session_id == session_id,
        )
    )
    participant = result.scalar_one_or_none()
    if participant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Участник не найден")

    await db.delete(participant)
    await db.commit()

    await manager.broadcast(session_id, {
        "type": "participant_left",
        "payload": {"participant_id": participant_id},
    })


@public_router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await get_session_or_404(session_id, db)

    if session.host_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")
    if session.status != "waiting":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отменить можно только сессию, которая ещё не началась",
        )

    session.status = "cancelled"
    await db.commit()

    await manager.broadcast(session_id, {"type": "session_cancelled", "payload": {}})


@public_router.get("/{session_id}/participants", response_model=list[ParticipantRead])
async def get_participants(session_id: int, db: AsyncSession = Depends(get_db)):
    await get_session_or_404(session_id, db)

    result = await db.execute(
        select(SessionParticipant).where(SessionParticipant.session_id == session_id)
    )

    return result.scalars().all()


@public_router.post("/{session_id}/next-question", response_model=QuestionRead)
async def next_question(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await get_session_or_404(session_id, db)

    if session.host_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")

    if session.status == "finished":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Сессия окончена")

    result = await db.execute(
        select(Question)
        .where(Question.quiz_id == session.quiz_id)
        .order_by(Question.order_index)
        .options(selectinload(Question.answer_options))
    )
    questions = result.scalars().all()

    if session.current_question_id is None:
        next_q = questions[0]
    else:
        idx = next(i for i, q in enumerate(questions) if q.id == session.current_question_id)
        if idx + 1 >= len(questions):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Вопросы закончились")
        next_q = questions[idx + 1]

    if session.status == "waiting":
        session.status = "active"
        session.started_at = func.now()

    session.current_question_id = next_q.id
    session.current_question_started_at = func.now()

    await db.commit()
    await db.refresh(session)

    payload = QuestionRead.model_validate(next_q).model_dump(
        mode="json",
        exclude={"answer_options": {"__all__": {"is_correct"}}},
    )

    await manager.broadcast(session.id, {"type": "new_question", "payload": payload})

    return next_q