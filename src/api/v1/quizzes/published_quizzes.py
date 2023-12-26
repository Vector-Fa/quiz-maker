from typing import Annotated

from fastapi import APIRouter, Path, Depends
from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers import (
    QuizController,
    UserAnswersController,
    QuestionController,
)
from src.app.repositories import (
    QuizRepository,
    QuestionRepository,
    UserAnswersRepository,
    ParticipantRepo,
)
from src.app.schemas.extra.success import MessageResponse
from src.app.schemas.extra.token import TokenData
from src.app.schemas.in_.quizzes import UserQuestionAnswersIn, QuizEnterPasswordIn
from src.app.schemas.in_.user_answers import UpdateParticipantAnswersIn
from src.app.schemas.out.quizzes import (
    PublishedQuizQuestionsOut,
    ParticipantsAnswersOut,
    QuizPasswordStatus,
    QuestionsByIdOut,
)
from src.app.schemas.out.user_answers import ParticipantAnswersOut
from src.app.utils.get_quiz import get_quiz_by_id
from src.core.access_control import access_control, is_quiz_owner, is_admin
from src.core.access_control.policies import check_quiz_password
from src.core.database import get_session
from src.core.fastapi.dependencies.auth import authentication_required

router = APIRouter(prefix="/pub")


@router.get(
    "/{quiz_path}/password-status",
    description="check whether quiz is locked by a password or not",
)
async def check_quiz_password_status(
    quiz_path: Annotated[str, Path(min_length=3, max_length=30)],
    db_session: AsyncSession = Depends(get_session),
) -> QuizPasswordStatus:
    quiz_repository = QuizRepository(db_session)
    return await QuizController(quiz_repository).check_quiz_password_status(
        quiz_path=quiz_path
    )


@router.post(
    "/{quiz_id}/get-questions",
    description="""get quiz questions if the quiz is activated & 
             check entered password if quiz is locked""",
)
async def get_published_quiz_questions(
    quiz_id: PositiveInt,
    quiz_password: QuizEnterPasswordIn,
    db_session: AsyncSession = Depends(get_session),
) -> PublishedQuizQuestionsOut:
    quiz_repository = QuizRepository(db_session)
    question_repository = QuestionRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, quiz_id)

    await access_control(
        (check_quiz_password,), quiz=quiz, entered_password=quiz_password.password
    )
    return await QuizController(quiz_repository).get_published_quiz_questions(
        quiz=quiz, question_repository=question_repository
    )


@router.post(
    "/{quiz_id}",
    description="if quiz started, participants can start answering to questions",
)
async def answer_quiz_questions(
    quiz_id: PositiveInt,
    user_answers: UserQuestionAnswersIn,
    db_session: AsyncSession = Depends(get_session),
) -> MessageResponse:
    quiz_repository = QuizRepository(db_session)
    question_repository = QuestionRepository(db_session)
    participant_repo = ParticipantRepo(db_session)

    return await QuizController(quiz_repository).answer_questions(
        user_answers=user_answers,
        question_repository=question_repository,
        participant_repo=participant_repo,
        quiz_id=quiz_id,
    )


@router.patch(
    "/{quiz_id}/update/user-answers",
    description="update participant answers if their answers is correct or not",
)
async def update_participant_answers(
    quiz_id: PositiveInt,
    participant_answers: UpdateParticipantAnswersIn,
    db_session: AsyncSession = Depends(get_session),
    token: TokenData = Depends(authentication_required),
) -> MessageResponse:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    user_answers_repository = UserAnswersRepository(db_session)
    return await UserAnswersController(user_answers_repository).update_participant_answers(
        participant_answers=participant_answers
    )


@router.get(
    "/{quiz_id}/all/answers",
    description="get the score of all participant answers for a quiz",
)
async def get_all_participants_answers_with_score(
    quiz_id: PositiveInt,
    db_session: AsyncSession = Depends(get_session),
    token: TokenData = Depends(authentication_required),
) -> ParticipantsAnswersOut:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    user_answers_repository = UserAnswersRepository(db_session)
    participant_repo = ParticipantRepo(db_session)
    question_repository = QuestionRepository(db_session)

    return await UserAnswersController(
        user_answers_repository
    ).get_participant_answers_with_score(
        quiz_id=quiz_id,
        participant_repo=participant_repo,
        question_repository=question_repository,
    )


@router.get(
    "/{quiz_id}/participant/{participant_id}/answers",
    description="get the score of one participant answers for a quiz",
)
async def get_participant_answers(
    quiz_id: PositiveInt,
    participant_id: PositiveInt,
    db_session: AsyncSession = Depends(get_session),
    token: TokenData = Depends(authentication_required),
) -> ParticipantAnswersOut:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    user_answers_repository = UserAnswersRepository(db_session)
    participant_repo = ParticipantRepo(db_session)
    return await UserAnswersController(user_answers_repository).get_participant_answers(
        quiz_id=quiz_id,
        participant_id=participant_id,
        participant_repo=participant_repo,
    )


@router.get(
    "/{quiz_id}/question/answers",
    description="get all the answers associated with the quiz",
)
async def get_question_answers(
    quiz_id: PositiveInt,
    db_session: AsyncSession = Depends(get_session),
    token: TokenData = Depends(authentication_required),
) -> QuestionsByIdOut:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    question_repository = QuestionRepository(db_session)
    return await QuestionController(question_repository).get_question_answers(
        quiz_id=quiz_id
    )
