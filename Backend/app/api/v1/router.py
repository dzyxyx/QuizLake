from fastapi import APIRouter
from app.api.v1.endpoints import auth, categories, quizzes, questions
from backend.app.api.v1.endpoints import quiz_sessions

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(questions.router, prefix="/quizzes/{quiz_id}/questions", tags=["questions"])
api_router.include_router(quiz_sessions.router, prefix="/quizzes/{quiz_id}/sessions", tags=["sessions"])
api_router.include_router(quiz_sessions.public_router, prefix="/sessions", tags=["quiz_sessions"])