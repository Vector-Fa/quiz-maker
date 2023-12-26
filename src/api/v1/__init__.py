from fastapi import APIRouter

from .quizzes import quizzes_router
from .users import users_router

v1_router = APIRouter()
v1_router.include_router(users_router, prefix='/user')
v1_router.include_router(quizzes_router, prefix='/quiz')

