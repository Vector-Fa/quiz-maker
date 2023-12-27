from pydantic import PositiveInt

from src.app.models.enums_ import QuestionType
from src.app.repositories import QuestionRepository
from src.app.schemas.extra.success import MessageResponse
from src.app.schemas.in_.quizzes import (
    AddMultipleOptionQuestionIn,
    UpdateMultipleOptionQuestionIn,
)
from src.app.schemas.out.quizzes import (
    DescriptiveQuestionOut,
    MultipleOptionQuestionOut,
    QuestionsOut,
    QuestionsByIdOut,
)


from src.core.excpetions import BadRequestException
from src.core.excpetions.database import ItemNotFoundError


class QuestionController:
    def __init__(self, question_repository: QuestionRepository):
        self.question_repository = question_repository

    async def add_short_descriptive_question(
        self,
        question_text: str,
        question_score: float,
        answer: str | None,
        quiz_id: int,
    ) -> DescriptiveQuestionOut:
        question = await self.question_repository.create_descriptive_question(
            question=question_text,
            quiz_id=quiz_id,
            answer=answer,
            question_type=QuestionType.DESCRIPTIVE_SHORT_ANSWER,
            question_score=question_score,
        )
        return DescriptiveQuestionOut.model_validate(question)

    async def add_long_descriptive_question(
        self,
        question_text: str,
        question_score: float,
        answer: str | None,
        quiz_id: int,
    ) -> DescriptiveQuestionOut:
        question = await self.question_repository.create_descriptive_question(
            question=question_text,
            quiz_id=quiz_id,
            answer=answer,
            question_type=QuestionType.DESCRIPTIVE_LONG_ANSWER,
            question_score=question_score,
        )
        return DescriptiveQuestionOut.model_validate(question)

    async def add_multiple_option_question(
        self, question: AddMultipleOptionQuestionIn
    ) -> MultipleOptionQuestionOut:
        new_question = await self.question_repository.create_multiple_option(
            question=question.question,
            quiz_id=question.quiz_id,
            options=question.options,
            question_score=question.score,
        )
        correct_option_index: PositiveInt = question.correct_option_index
        # get the option_id (database) at the index user specified is the correct option
        correct_option_id = new_question.multiple_options[correct_option_index].id

        await self.question_repository.create_correct_option(
            question_id=new_question.id, option_id=correct_option_id
        )
        return MultipleOptionQuestionOut.model_validate(new_question)

    async def delete_question_by_id(self, question_id: int) -> MessageResponse:
        try:
            await self.question_repository.delete_by_id(question_id=question_id)
        except ItemNotFoundError:
            raise BadRequestException("question not found", "question_not_found")

        return MessageResponse(message="question deleted")

    async def get_all_quiz_questions(self, quiz_id: int) -> QuestionsOut:
        question_objects = await self.question_repository.get_all_quiz_questions(
            quiz_id
        )

        return QuestionsOut(quiz_id=quiz_id, questions=question_objects)  # noqa

    async def update_descriptive_question(
        self,
        question_id: int,
        question_text: str,
        answer: str | None,
        new_score: float,
    ) -> DescriptiveQuestionOut:
        try:
            question = await self.question_repository.get_descriptive_by_id(
                question_id=question_id
            )
        except ItemNotFoundError:
            raise BadRequestException("question not found", "question_not_found")

        updated_question = await self.question_repository.update_descriptive_question(
            question=question,
            question_text=question_text,
            answer=answer,
            new_score=new_score,
        )
        return DescriptiveQuestionOut.model_validate(updated_question)

    async def get_question_answers(self, quiz_id: int) -> QuestionsByIdOut:
        questions = await self.question_repository.get_questions_with_answers(quiz_id)
        questions_out = {q.id: q for q in questions}
        return QuestionsByIdOut(questions=questions_out)

    async def update_multiple_option_question(
        self, question_id: int, question: UpdateMultipleOptionQuestionIn
    ) -> MultipleOptionQuestionOut:
        question_object = await self.question_repository.get_multiple_option_by_id(
            question_id=question_id
        )

        updated_question = (
            await self.question_repository.update_multiple_option_question(
                question=question_object,
                question_text=question.text,
                options_in=question.options,
                new_score=question.new_score,
            )
        )
        try:
            correct_option_id = updated_question.multiple_options[
                question.correct_option_index
            ].id
        except IndexError:
            raise BadRequestException(
                "index out of range", "correct_answer_index_out_of_range"
            )

        await self.question_repository.update_correct_option(
            option_id=correct_option_id, question_id=updated_question.id
        )
        return MultipleOptionQuestionOut.model_validate(updated_question)
