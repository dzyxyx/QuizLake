from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import User, Quiz, Question, QuizSession, SessionParticipant
from app.schemas.user import (
    UserRead,
    UserUpdate,
    UserStats,
    ParticipationHistoryItem,
    HostedSessionHistoryItem,
)
from app.api.deps import get_current_user
from app.core.security import hash_password


router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    update_data = user_data.model_dump(exclude_unset=True, exclude={"password"})

    if user_data.email is not None and user_data.email != current_user.email:
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже занят")

    if user_data.nickname is not None and user_data.nickname != current_user.nickname:
        result = await db.execute(select(User).where(User.nickname == user_data.nickname))
        if result.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Никнейм уже занят")

    for field, value in update_data.items():
        setattr(current_user, field, value)

    if user_data.password:
        current_user.password_hash = hash_password(user_data.password)

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/me/stats", response_model=UserStats)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    created = await db.scalar(
        select(func.count(func.distinct(Quiz.id)))
        .select_from(Quiz)
        .join(QuizSession, QuizSession.quiz_id == Quiz.id)
        .where(Quiz.owner_id == current_user.id, QuizSession.status == "finished")
    )

    hosted_sessions_count = await db.scalar(
        select(func.count())
        .select_from(QuizSession)
        .where(QuizSession.host_id == current_user.id, QuizSession.status == "finished")
    )

    result = await db.execute(
        select(SessionParticipant, QuizSession.quiz_id)
        .join(QuizSession, SessionParticipant.session_id == QuizSession.id)
        .where(SessionParticipant.user_id == current_user.id, QuizSession.status == "finished")
    )
    rows = result.all()

    played = len(rows)
    wins = sum(1 for participant, _ in rows if participant.final_rank == 1)

    percentages: list[float] = []
    for participant, quiz_id in rows:
        total_questions = await db.scalar(
            select(func.count()).select_from(Question).where(Question.quiz_id == quiz_id)
        )
        if total_questions:
            percentages.append(participant.correct_answers_count / total_questions * 100)

    avg_score_percent = round(sum(percentages) / len(percentages)) if percentages else 0

    return UserStats(
        played=played,
        wins=wins,
        created=created or 0,
        hosted_sessions_count=hosted_sessions_count or 0,
        avg_score_percent=avg_score_percent,
    )


@router.get("/me/participation-history", response_model=list[ParticipationHistoryItem])
async def get_participation_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SessionParticipant, QuizSession, Quiz.title)
        .join(QuizSession, SessionParticipant.session_id == QuizSession.id)
        .join(Quiz, QuizSession.quiz_id == Quiz.id)
        .where(SessionParticipant.user_id == current_user.id, QuizSession.status == "finished")
        .order_by(QuizSession.ended_at.desc())
    )
    rows = result.all()

    items = []
    for participant, session, quiz_title in rows:
        participants_count = await db.scalar(
            select(func.count())
            .select_from(SessionParticipant)
            .where(SessionParticipant.session_id == session.id)
        )
        items.append(
            ParticipationHistoryItem(
                session_id=session.id,
                room_code=session.room_code,
                quiz_title=quiz_title,
                ended_at=session.ended_at,
                participants_count=participants_count or 0,
                final_rank=participant.final_rank,
            )
        )
    return items


@router.get("/me/hosted-history", response_model=list[HostedSessionHistoryItem])
async def get_hosted_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(QuizSession, Quiz.title)
        .join(Quiz, QuizSession.quiz_id == Quiz.id)
        .where(QuizSession.host_id == current_user.id, QuizSession.status == "finished")
        .order_by(QuizSession.ended_at.desc())
    )
    rows = result.all()

    items = []
    for session, quiz_title in rows:
        participants_count = await db.scalar(
            select(func.count())
            .select_from(SessionParticipant)
            .where(SessionParticipant.session_id == session.id)
        )
        items.append(
            HostedSessionHistoryItem(
                session_id=session.id,
                room_code=session.room_code,
                quiz_title=quiz_title,
                ended_at=session.ended_at,
                participants_count=participants_count or 0,
            )
        )
    return items
