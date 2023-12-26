from src.app.models import Question
from src.app.schemas.in_.quizzes import (
    UserMultipleOptionAnswersIn,
    UserDescriptiveAnswersIn,
)
from src.core.excpetions import BadRequestException


def validate_answer_option_questions(
    questions: list[Question], user_answers: list[UserMultipleOptionAnswersIn]
) -> None:
    """check if user multiple option answers are compatible with the quiz questions"""
    if len(questions) != len(user_answers):
        raise BadRequestException("question missing from answer", "question_missing")

    for question, user_answer in zip(questions, user_answers):
        option_ids = [option.id for option in question.multiple_options]
        if user_answer.option_id not in option_ids:
            raise BadRequestException(
                message=user_answer.option_id, type_="wrong_option_id"
            )


def validate_answer_descriptive_question(
    questions: list[Question], user_answers: list[UserDescriptiveAnswersIn]
) -> None:
    if len(questions) != len(user_answers):
        raise BadRequestException("question missing from answer", "question_missing")
