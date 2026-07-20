from fastapi import APIRouter, HTTPException, Depends, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import QuizSession, User, SessionParticipant
from app.schemas.quiz_session import QuizSessionCreate, QuizSessionRead
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

    if current_user is not None:
        existing = await db.execute(
            select(SessionParticipant).where(
                SessionParticipant.session_id == session.id,
                SessionParticipant.user_id == current_user.id,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Вы уже в этой комнате")
    
    new_participant = SessionParticipant(
        session_id=session.id,
        user_id=user_id,
        display_name=join_data.display_name,
        avatar_url=join_data.avatar_url,
    )

    db.add(new_participant)
    await db.commit()
    await db.refresh(new_participant)

    return new_participant


@public_router.get("/{session_id}/participants", response_model=list[ParticipantRead])
async def get_participants(session_id: int, db: AsyncSession = Depends(get_db)):
    await get_session_or_404(session_id, db)

    result = await db.execute(
        select(SessionParticipant).where(SessionParticipant.session_id == session_id)
    )

    return result.scalars().all()