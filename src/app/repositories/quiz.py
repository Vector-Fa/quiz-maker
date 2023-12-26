from typing import Sequence

from sqlalchemy import (
    func,
    select,
    update,
    RowMapping,
    exists,
)
from sqlalchemy.orm import selectinload

from src.core.excpetions.database import ItemNotFoundError
from src.core.repository.base import BaseRepository

from ..models import Question, Quiz
from ...core.types.database_out import RowCount


class QuizRepository(BaseRepository[Quiz]):
    async def create_quiz(self, title: str, user_id: int, quiz_path: str) -> Quiz:
        quiz = await self._create_and_refresh(
            title=title, owner_id=user_id, quiz_path=quiz_path
        )
        return quiz

    async def get_user_quizzes(self, user_id: int) -> Sequence[RowMapping]:
        query = (
            select(Quiz, func.count(Question.id).label("question_count"))
            .where(Quiz.owner_id == user_id)
            .outerjoin(Question, Quiz.id == Question.quiz_id)
            .group_by(Quiz.id)
        )
        return await self._mappings_all(query)

    async def get_quiz_by_owner_id(self, quiz_id: int, user_id: int) -> Quiz:
        query = select(Quiz).where(Quiz.id == quiz_id & (Quiz.owner_id == user_id))
        return await self._one(query)

    async def delete_by_id(self, quiz_id: int) -> bool:
        query = self._delete_by("id", quiz_id)
        result = await self._execute(query)
        await self.session.commit()
        if not result.rowcount:
            raise ItemNotFoundError
        return True

    async def get_by_id(self, quiz_id: int) -> Quiz:
        query = self._get_by("id", quiz_id)
        return await self._one(query)

    async def get_by_id_with_questions(self, quiz_id: int) -> Quiz:
        query = self._get_by("id", quiz_id).options(selectinload(Quiz.questions))
        return await self._one(query)

    async def update_quiz_password(
        self, quiz_id: int, password: str, quiz_lock: bool
    ) -> RowCount:
        query = (
            update(Quiz)
            .where(Quiz.id == quiz_id)
            .values(password=password, need_password=quiz_lock)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount

    async def update_settings(self, quiz_id: int, **kwargs) -> Quiz:
        query = update(Quiz).where(Quiz.id == quiz_id).values(**kwargs).returning(Quiz)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one()

    async def get_by_path(self, quiz_path: str) -> Quiz:
        query = self._get_by("quiz_path", quiz_path)
        return await self._one(query)

    async def quiz_path_exists(self, quiz_path: str) -> bool:
        query = select(exists(select(Quiz).where(Quiz.quiz_path == quiz_path)))
        result = await self._execute(query)
        return result.scalar_one()
