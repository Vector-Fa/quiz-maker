from fastapi import APIRouter

from .quizzes import router as quiz_router
from .published_quizzes import router as public_quiz_router

quizzes_router = APIRouter()
quizzes_router.include_router(quiz_router, tags=['Quizzes'])
quizzes_router.include_router(public_quiz_router, tags=['Published Quizzes'])
