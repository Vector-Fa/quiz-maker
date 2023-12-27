from src.app.models import Quiz
from src.app.repositories import QuizRepository
from src.core.excpetions import BadRequestException
from src.core.excpetions.database import ItemNotFoundError


async def get_quiz_by_id(quiz_repository: QuizRepository, quiz_id: int) -> Quiz:
    try:
        quiz = await quiz_repository.get_by_id(quiz_id=quiz_id)
    except ItemNotFoundError:
        raise BadRequestException("quiz not found", "no_quiz_found")

    return quiz
