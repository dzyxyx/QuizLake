from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import (
    Question,
    SessionParticipant,
    ParticipantAnswer,
    ParticipantAnswerOption,
    User,
)
from app.schemas.participant_answer import AnswerSubmit, AnswerResult
from app.api.deps import get_session_or_404, get_current_user, get_current_user_optional
from app.websockets.manager import manager


router = APIRouter()


@router.post(
    "/{session_id}/participants/{participant_id}/submit-answer",
    response_model=AnswerResult,
    status_code=status.HTTP_201_CREATED,
)
async def submit_answer(
    session_id: int,
    participant_id: int,
    answer_data: AnswerSubmit,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    session = await get_session_or_404(session_id, db)

    if session.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Сессия не активна")
    if session.current_question_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нет активного вопроса")

    result = await db.execute(
        select(SessionParticipant).where(
            SessionParticipant.id == participant_id,
            SessionParticipant.session_id == session_id,
        )
    )
    participant = result.scalar_one_or_none()
    if participant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Участник не найден в этой сессии")

    if participant.user_id is not None:
        if current_user is None or current_user.id != participant.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нельзя отвечать за другого участника")

    result = await db.execute(
        select(Question)
        .where(Question.id == session.current_question_id)
        .options(selectinload(Question.answer_options))
    )
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден")

    now = datetime.now(timezone.utc)
    if question.time_limit_sec is not None and session.current_question_started_at is not None:
        deadline = session.current_question_started_at + timedelta(seconds=question.time_limit_sec)
        if now > deadline:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Время на ответ истекло")

    existing = await db.execute(
        select(ParticipantAnswer).where(
            ParticipantAnswer.participant_id == participant_id,
            ParticipantAnswer.question_id == question.id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Вы уже ответили на этот вопрос")

    valid_option_ids = {option.id for option in question.answer_options}
    selected_ids = set(answer_data.selected_option_ids)
    if not selected_ids or not selected_ids.issubset(valid_option_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Некорректные варианты ответа")
    if question.question_type == "single" and len(selected_ids) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Для этого вопроса нужно выбрать ровно один вариант",
        )

    correct_option_ids = {option.id for option in question.answer_options if option.is_correct}
    is_correct = selected_ids == correct_option_ids

    response_time_ms = None
    if session.current_question_started_at is not None:
        response_time_ms = max(0, int((now - session.current_question_started_at).total_seconds() * 1000))

    points_awarded = 0
    if is_correct:
        base_points = question.points or 1000
        if question.time_limit_sec and response_time_ms is not None:
            time_limit_ms = question.time_limit_sec * 1000
            speed_ratio = max(0.0, 1 - response_time_ms / time_limit_ms)
            points_awarded = round(base_points * (0.5 + 0.5 * speed_ratio))
        else:
            points_awarded = base_points

    new_answer = ParticipantAnswer(
        session_id=session_id,
        question_id=question.id,
        participant_id=participant_id,
        is_correct=is_correct,
        response_time_ms=response_time_ms,
        points_awarded=points_awarded,
        answered_at=now,
    )
    db.add(new_answer)
    await db.flush()

    for option_id in selected_ids:
        db.add(ParticipantAnswerOption(participant_answer_id=new_answer.id, option_id=option_id))

    participant.total_score += points_awarded
    if is_correct:
        participant.correct_answers_count += 1

    await db.commit()
    await db.refresh(new_answer)

    total_participants = await db.scalar(
        select(func.count()).select_from(SessionParticipant).where(SessionParticipant.session_id == session_id)
    )
    answered_count = await db.scalar(
        select(func.count()).select_from(ParticipantAnswer).where(
            ParticipantAnswer.session_id == session_id,
            ParticipantAnswer.question_id == question.id,
        )
    )
    await manager.broadcast(session_id, {
        "type": "participant_answered",
        "payload": {"answered_count": answered_count, "total_participants": total_participants},
    })

    return AnswerResult(
        id=new_answer.id,
        session_id=new_answer.session_id,
        question_id=new_answer.question_id,
        participant_id=new_answer.participant_id,
        selected_option_ids=list(selected_ids),
        is_correct=new_answer.is_correct,
        response_time_ms=new_answer.response_time_ms,
        points_awarded=new_answer.points_awarded,
        answered_at=new_answer.answered_at,
    )


@router.post("/{session_id}/reveal-answer")
async def reveal_answer(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await get_session_or_404(session_id, db)

    if session.host_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")
    if session.current_question_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нет активного вопроса")

    result = await db.execute(
        select(Question)
        .where(Question.id == session.current_question_id)
        .options(selectinload(Question.answer_options))
    )
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден")

    correct_option_ids = [option.id for option in question.answer_options if option.is_correct]

    option_counts_result = await db.execute(
        select(ParticipantAnswerOption.option_id, func.count())
        .join(ParticipantAnswer, ParticipantAnswerOption.participant_answer_id == ParticipantAnswer.id)
        .where(ParticipantAnswer.session_id == session_id, ParticipantAnswer.question_id == question.id)
        .group_by(ParticipantAnswerOption.option_id)
    )
    counts_by_option = dict(option_counts_result.all())
    total_answered = sum(counts_by_option.values())

    option_stats = [
        {
            "option_id": option.id,
            "option_text": option.option_text,
            "is_correct": option.is_correct,
            "selected_count": counts_by_option.get(option.id, 0),
            "selected_percent": (
                round(counts_by_option.get(option.id, 0) / total_answered * 100) if total_answered else 0
            ),
        }
        for option in question.answer_options
    ]

    result = await db.execute(
        select(SessionParticipant)
        .where(SessionParticipant.session_id == session_id)
        .order_by(SessionParticipant.total_score.desc())
    )
    participants = result.scalars().all()

    leaderboard = [
        {
            "participant_id": p.id,
            "display_name": p.display_name,
            "total_score": p.total_score,
            "correct_answers_count": p.correct_answers_count,
        }
        for p in participants
    ]

    payload = {
        "question_id": question.id,
        "correct_option_ids": correct_option_ids,
        "option_stats": option_stats,
        "leaderboard": leaderboard,
    }

    await manager.broadcast(session_id, {"type": "answer_revealed", "payload": payload})

    return payload


@router.post("/{session_id}/end-game")
async def end_game(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await get_session_or_404(session_id, db)

    if session.host_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")
    if session.status == "finished":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Игра уже завершена")

    result = await db.execute(
        select(SessionParticipant)
        .where(SessionParticipant.session_id == session_id)
        .order_by(SessionParticipant.total_score.desc())
    )
    participants = result.scalars().all()

    for rank, participant in enumerate(participants, start=1):
        participant.final_rank = rank

    session.status = "finished"
    session.ended_at = func.now()

    await db.commit()

    leaderboard = [
        {
            "participant_id": p.id,
            "display_name": p.display_name,
            "total_score": p.total_score,
            "correct_answers_count": p.correct_answers_count,
            "final_rank": p.final_rank,
        }
        for p in participants
    ]

    await manager.broadcast(session_id, {"type": "game_ended", "payload": {"leaderboard": leaderboard}})

    return {"leaderboard": leaderboard}
