from sqlalchemy import select, update, func, RowMapping
from sqlalchemy.orm import selectinload, joinedload

from src.app.models import Descriptive, Question, MultipleOption, CorrectOption
from src.app.models.enums_ import QuestionType
from src.app.schemas.in_.quizzes import MultipleOptionUpdateIn, MultipleOptionIn
from src.core.excpetions.database import ItemNotFoundError
from src.core.repository.base import BaseRepository


class QuestionRepository(BaseRepository[Question]):
    async def create_descriptive_question(
        self,
        question: str,
        quiz_id: int,
        answer: str | None,
        question_type: QuestionType,
        question_score: float,
    ) -> Question:
        question = Question(
            text=question,
            question_type=question_type,
            quiz_id=quiz_id,
            score=question_score,
        )
        if answer:
            question.descriptive = Descriptive(answer=answer)
        self.session.add(question)
        await self.session.commit()
        await self.session.refresh(question, attribute_names=["descriptive"])
        return question

    async def create_multiple_option(
        self,
        question: str,
        quiz_id: int,
        options: list[MultipleOptionIn],
        question_score: float,
    ) -> Question:
        options = [MultipleOption(text=answer.text) for answer in options]
        question = Question(
            text=question,
            question_type=QuestionType.MULTIPLE_OPTIONS,
            quiz_id=quiz_id,
            multiple_options=options,
            score=question_score,
        )
        self.session.add(question)
        await self.session.commit()
        await self.session.refresh(question, attribute_names=["multiple_options"])
        return question

    async def create_correct_option(self, option_id: int, question_id: int) -> None:
        correct_option = CorrectOption(option_id=option_id, question_id=question_id)
        self.session.add(correct_option)
        await self.session.commit()

    async def delete_by_id(self, question_id: int) -> bool:
        query = self._delete_by("id", question_id)
        result = await self._execute(query)
        await self.session.commit()
        if not result.rowcount:
            raise ItemNotFoundError
        return True

    async def get_all_quiz_questions(self, quiz_id: int) -> list[Question]:
        query = (
            select(Question)
            .options(
                selectinload(Question.multiple_options),
                selectinload(Question.descriptive),
                selectinload(Question.correct_option),
            )
            .where(Question.quiz_id == quiz_id)
        )
        return await self._all(query)

    async def get_descriptive_by_id(self, question_id: int) -> Question:
        query = (
            select(Question)
            .where(Question.id == question_id)
            .options(joinedload(Question.descriptive))
        )
        return await self._one(query)

    async def update_descriptive_question(
        self,
        question: Question,
        question_text: str,
        answer: str | None,
        new_score: float,
    ) -> Question:
        question.text = question_text
        question.score = new_score
        if question.descriptive:
            question.descriptive.answer = answer
        else:
            question.descriptive = Descriptive(answer=answer)

        await self.session.commit()
        await self.session.refresh(question)
        return question

    async def get_multiple_option_by_id(self, question_id: int) -> Question:
        query = (
            select(Question)
            .where(Question.id == question_id)
            .options(
                selectinload(Question.multiple_options),
                joinedload(Question.correct_option),
            )
        )
        return await self._one(query)

    async def update_correct_option(
        self, option_id: int, question_id: int
    ) -> CorrectOption:
        query = (
            update(CorrectOption)
            .where(CorrectOption.question_id == question_id)
            .values(option_id=option_id)
            .returning(CorrectOption)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one()

    async def get_descriptive_questions_by_ids(
        self, question_ids: list[int], quiz_id: int
    ) -> list[Question]:
        query = select(Question).where(
            Question.id.in_(question_ids)
            & (Question.quiz_id == quiz_id)
            & (Question.question_type != QuestionType.MULTIPLE_OPTIONS)
        )
        return await self._all(query)

    async def get_options_questions_by_ids(
        self, question_ids: list[int], quiz_id: int
    ) -> list[Question]:
        query = (
            select(Question)
            .options(selectinload(Question.multiple_options))
            .where(
                Question.id.in_(question_ids)
                & (Question.quiz_id == quiz_id)
                & (Question.question_type == QuestionType.MULTIPLE_OPTIONS)
            )
        )
        return await self._all(query)

    async def get_questions_with_answers(self, quiz_id: int) -> list[Question]:
        query = (
            select(Question)
            .options(
                selectinload(Question.descriptive),
                selectinload(Question.correct_option),
            )
            .where(Question.quiz_id == quiz_id)
        )
        return await self._all(query)

    async def total_quiz_questions_score(self, quiz_id: int) -> RowMapping:
        query = select(func.sum(Question.score).label("total_quiz_score")).where(
            Question.quiz_id == quiz_id
        )
        return await self._mappings_one(query)

    async def update_multiple_option_question(
        self,
        question: Question,
        question_text: str,
        options_in: list[MultipleOptionUpdateIn],
        new_score: float,
    ) -> Question:
        """
        Update choices of a question in the database based on these rules:
        - For each item in the options_in parameter:
            - If the option has an id and text, update the row.
            - If the option has only text, create one.
            - If an option in the database doesn't exist in the user input, delete it.
        """
        question.text, question.score = question_text, new_score

        options_to_change: dict[int, str] = {}
        for option in options_in:
            if option.id is None:
                question.multiple_options.append(MultipleOption(text=option.text))
            else:
                options_to_change[option.id] = option.text

        for option_db in list(question.multiple_options):
            if option_db.id in options_to_change:
                option_db.text = options_to_change[option_db.id]
            elif option_db.id is not None:
                question.multiple_options.remove(option_db)

        await self.session.commit()
        await self.session.refresh(question)
        return question
