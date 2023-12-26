import random

from pydantic import PositiveInt

from src.app.repositories import (
    QuizRepository,
    QuestionRepository,
    ParticipantRepo,
)
from src.core.excpetions import BadRequestException
from src.core.excpetions.database import ItemNotFoundError
from src.core.security.password import PasswordHandler
from ..models import Quiz

from ..schemas.extra.success import MessageResponse
from ..schemas.in_.quizzes import QuizSettingIn, UserQuestionAnswersIn
from ..schemas.out.quizzes import (
    CreatedQuizOut,
    QuizSettingOut,
    PublishedQuizQuestionsOut,
    QuizPasswordStatus,
    CreatedQuizOutList,
    QuizInfoOut,
    QuizActivationStatus,
)

# from ..utils.get_question_models import get_published_question_model_by_type
from ..utils.quiz_validations import (
    validate_quiz_for_activation,
    validate_quiz_is_started,
    check_quiz_dates,
)
from ..utils.random_string import get_random_string
from ..utils.validate_questions import (
    validate_answer_option_questions,
    validate_answer_descriptive_question,
)


class QuizController:
    password_handler = PasswordHandler

    def __init__(self, quiz_repository: QuizRepository):
        self.quiz_repository = quiz_repository

    async def create_quiz(self, quiz_title: str, user_id: int) -> QuizInfoOut:
        created_quiz = await self.quiz_repository.create_quiz(
            title=quiz_title, user_id=user_id, quiz_path=get_random_string()
        )

        return QuizInfoOut(id=created_quiz.id, title=created_quiz.title)

    async def get_user_quizzes(self, user_id: int) -> list[CreatedQuizOut]:
        quiz_objects = await self.quiz_repository.get_user_quizzes(user_id=user_id)
        quizzes = CreatedQuizOutList.validate_python(quiz_objects)
        return quizzes

    async def delete_quiz_by_id(self, quiz_id: int) -> MessageResponse:
        try:
            await self.quiz_repository.delete_by_id(quiz_id=quiz_id)
        except ItemNotFoundError:
            raise BadRequestException("Bad action", "bad_action")

        return MessageResponse(message="deleted")

    async def set_quiz_password(
        self, password: str, quiz_lock: bool, quiz_id: int
    ) -> MessageResponse:
        quiz = await self.quiz_repository.update_quiz_password(
            password=password, quiz_lock=quiz_lock, quiz_id=quiz_id
        )
        if quiz:
            return MessageResponse(message="changed successfully")

    async def get_quiz_settings(self, quiz: Quiz) -> QuizSettingOut:
        return QuizSettingOut.model_validate(quiz)

    async def update_quiz_settings(
        self, quiz_id: int, settings: QuizSettingIn
    ) -> QuizSettingOut:
        settings = settings.model_dump(exclude_none=True)
        quiz_path_in = settings.get("quiz_path")
        if quiz_path_in:
            path_exists = await self.quiz_repository.quiz_path_exists(quiz_path_in)
            if path_exists:
                raise BadRequestException("quiz path already exists", "path_exists")

        updated_quiz = await self.quiz_repository.update_settings(
            quiz_id=quiz_id, **settings
        )
        return QuizSettingOut.model_validate(updated_quiz)

    async def change_quiz_activation(self, quiz_id: int) -> QuizActivationStatus:
        quiz = await self.quiz_repository.get_by_id_with_questions(quiz_id=quiz_id)

        if quiz.is_active:
            await self.quiz_repository.update_settings(quiz_id=quiz_id, is_active=False)
            return QuizActivationStatus(message="quiz deactivated", is_active=False)
        else:
            validate_quiz_for_activation(quiz=quiz)
            await self.quiz_repository.update_settings(quiz_id=quiz_id, is_active=True)
            return QuizActivationStatus(message="quiz activated", is_active=True)

    async def get_published_quiz_questions(
        self, quiz: Quiz, question_repository: QuestionRepository
    ) -> PublishedQuizQuestionsOut:
        validate_quiz_is_started(quiz=quiz)

        question_objects = await question_repository.get_all_quiz_questions(
            quiz_id=quiz.id
        )
        if quiz.shuffle_options:
            random.shuffle(question_objects)

        return PublishedQuizQuestionsOut(
            questions=question_objects,  # type: ignore
            quiz_id=quiz.id,
            quiz_title=quiz.title,
            end_at=quiz.end_at,
        )

    async def check_quiz_password_status(self, quiz_path: str) -> QuizPasswordStatus:
        try:
            quiz = await self.quiz_repository.get_by_path(quiz_path=quiz_path)
        except ItemNotFoundError:
            raise BadRequestException("quiz not found", "quiz_not_found")

        validate_quiz_is_started(quiz=quiz)
        return QuizPasswordStatus(need_password=quiz.need_password, quiz_id=quiz.id)

    async def answer_questions(
        self,
        user_answers: UserQuestionAnswersIn,
        question_repository: QuestionRepository,
        participant_repo: ParticipantRepo,
        quiz_id: int,
    ) -> MessageResponse:
        """
        get participant answers on a quiz and validate the question of answers exist on
         database and connected to that particular quiz then save participant info and
          its answers
        """
        quiz = await self.quiz_repository.get_by_id(quiz_id)
        check_quiz_dates(quiz.start_at, quiz.end_at)

        descriptive_question_ids: list[int] = [
            q.question_id for q in user_answers.descriptive
        ]
        multiple_options_question_ids: list[int] = [
            q.question_id for q in user_answers.multiple_options
        ]

        descriptive_questions = (
            await question_repository.get_descriptive_questions_by_ids(
                question_ids=descriptive_question_ids, quiz_id=quiz_id
            )
        )
        multiple_option_questions = (
            await question_repository.get_options_questions_by_ids(
                question_ids=multiple_options_question_ids, quiz_id=quiz_id
            )
        )

        validate_answer_option_questions(
            questions=multiple_option_questions,
            user_answers=user_answers.multiple_options,
        )
        validate_answer_descriptive_question(
            questions=descriptive_questions, user_answers=user_answers.descriptive
        )
        unique_username = (
            f"{user_answers.participant_info.username}" f"+{get_random_string()}"
        )
        await participant_repo.add_participant_info_with_answers(
            username=unique_username,
            quiz_id=quiz_id,
            descriptive_answers=user_answers.descriptive,
            multiple_option_answers=user_answers.multiple_options,
        )
        return MessageResponse(message="accepted")

