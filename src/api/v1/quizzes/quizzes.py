
from fastapi import APIRouter, Depends
from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers import QuestionController, QuizController
from src.app.repositories import QuizRepository, QuestionRepository
from src.app.schemas.extra.success import MessageResponse
from src.app.schemas.extra.token import TokenData
from src.app.schemas.in_.quizzes import (
    AddShortDescriptiveQuestionIn,
    CreateQuizIn,
    AddMultipleOptionQuestionIn,
    AddLongDescriptiveQuestionIn,
    QuizPasswordIn,
    QuizSettingIn,
    UpdateDescriptiveQuestionIn,
    UpdateMultipleOptionQuestionIn,
)
from src.app.schemas.out.quizzes import (
    CreatedQuizOut,
    DescriptiveQuestionOut,
    MultipleOptionQuestionOut,
    QuestionsOut,
    QuizSettingOut,
    QuizInfoOut,
    QuizActivationStatus,
)
from src.app.utils.get_quiz import get_quiz_by_id
from src.core.access_control import access_control, is_quiz_owner, is_admin
from src.core.database import get_session
from src.core.fastapi.dependencies.auth import authentication_required

router = APIRouter()


@router.post("/create")
async def create_quiz(
    quiz_in: CreateQuizIn,
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> QuizInfoOut:
    quiz_repository = QuizRepository(db_session)
    return await QuizController(quiz_repository).create_quiz(
        quiz_title=quiz_in.title, user_id=token.user_id
    )


@router.get("/all", description="get all quizzes that user created")
async def get_user_quizzes(
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> list[CreatedQuizOut]:
    quiz_repository = QuizRepository(db_session)
    return await QuizController(quiz_repository).get_user_quizzes(user_id=token.user_id)


@router.delete("/delete/{quiz_id}", description="delete a quiz by id")
async def delete_quiz(
    quiz_id: PositiveInt,
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> MessageResponse:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    return await QuizController(quiz_repository).delete_quiz_by_id(quiz_id=quiz_id)


@router.post(
    "/add/question/descriptive-short",
    description="create descriptive question with short answer",
)
async def add_short_descriptive_question(
    question: AddShortDescriptiveQuestionIn,
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> DescriptiveQuestionOut:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, question.quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    question_repository = QuestionRepository(db_session)
    return await QuestionController(question_repository).add_short_descriptive_question(
        question_text=question.question,
        answer=question.answer,
        quiz_id=question.quiz_id,
        question_score=question.score,
    )


@router.post(
    "/add/question/descriptive-long",
    description="create descriptive question with long answer",
)
async def add_long_descriptive_question(
    question: AddLongDescriptiveQuestionIn,
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> DescriptiveQuestionOut:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, question.quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    question_repository = QuestionRepository(db_session)
    return await QuestionController(question_repository).add_long_descriptive_question(
        question_text=question.question,
        answer=question.answer,
        quiz_id=question.quiz_id,
        question_score=question.score,
    )


@router.post(
    "/add/question/multiple-option", description="create multiple option question"
)
async def add_multiple_option_question(
    question: AddMultipleOptionQuestionIn,
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> MultipleOptionQuestionOut:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, question.quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    question_repository = QuestionRepository(db_session)
    return await QuestionController(question_repository).add_multiple_option_question(
        question=question
    )


@router.get(
    "/{quiz_id}/questions", description="get all questions that is associated with quiz"
)
async def get_all_quiz_questions(
    quiz_id: PositiveInt,
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> QuestionsOut:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    question_repository = QuestionRepository(db_session)
    return await QuestionController(question_repository).get_all_quiz_questions(
        quiz_id=quiz_id
    )


@router.delete("/delete/question/{question_id}/quiz/{quiz_id}")
async def delete_question_by_id(
    quiz_id: PositiveInt,
    question_id: PositiveInt,
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> MessageResponse:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    question_repository = QuestionRepository(db_session)
    return await QuestionController(question_repository).delete_question_by_id(
        question_id=question_id
    )


@router.post("/set/password/{quiz_id}")
async def set_quiz_password(
    quiz_id: PositiveInt,
    password_setting: QuizPasswordIn,
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> MessageResponse:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    return await QuizController(quiz_repository).set_quiz_password(
        password=password_setting.password,
        quiz_lock=password_setting.quiz_lock,
        quiz_id=quiz_id,
    )


@router.patch("/{quiz_id}", description="make a partial update for quiz settings")
async def update_quiz_settings(
    quiz_id: PositiveInt,
    quiz_setting: QuizSettingIn,
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> QuizSettingOut:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    return await QuizController(quiz_repository).update_quiz_settings(
        quiz_id=quiz_id, settings=quiz_setting
    )


@router.get("/{quiz_id}")
async def get_quiz_settings(
    quiz_id: PositiveInt,
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> QuizSettingOut:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    return await QuizController(quiz_repository).get_quiz_settings(quiz=quiz)


@router.post(
    "/{quiz_id}/change-activation-status",
    description="flip quiz activation status whenever router is called",
)
async def change_quiz_activation_status(
    quiz_id: PositiveInt,
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> QuizActivationStatus:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    return await QuizController(quiz_repository).change_quiz_activation(quiz_id=quiz_id)


@router.put("/{quiz_id}/edit/question/{question_id}/descriptive")
async def update_descriptive_question(
    quiz_id: PositiveInt,
    question_id: PositiveInt,
    question: UpdateDescriptiveQuestionIn,
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> DescriptiveQuestionOut:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    question_repository = QuestionRepository(db_session)
    return await QuestionController(question_repository).update_descriptive_question(
        question_id=question_id,
        question_text=question.text,
        answer=question.answer,
        new_score=question.new_score,
    )


@router.put("/{quiz_id}/edit/question/{question_id}/multiple-option")
async def update_multiple_option_question(
    quiz_id: PositiveInt,
    question_id: PositiveInt,
    question: UpdateMultipleOptionQuestionIn,
    token: TokenData = Depends(authentication_required),
    db_session: AsyncSession = Depends(get_session),
) -> MultipleOptionQuestionOut:
    quiz_repository = QuizRepository(db_session)
    quiz = await get_quiz_by_id(quiz_repository, quiz_id)
    await access_control((is_admin, is_quiz_owner), user_info=token, quiz=quiz)

    question_repository = QuestionRepository(db_session)
    return await QuestionController(
        question_repository
    ).update_multiple_option_question(question_id=question_id, question=question)
