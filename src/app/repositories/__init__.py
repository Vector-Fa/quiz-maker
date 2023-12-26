from functools import partial

from .question import QuestionRepository
from .quiz import QuizRepository
from .user import UserRepository
from .user_answers import UserAnswersRepository
from .participant import ParticipantRepo

from ..models import Question, Quiz, User, Participant, UserDescriptiveAnswer

QuestionRepository = partial(QuestionRepository, Question)
QuizRepository = partial(QuizRepository, Quiz)
UserRepository = partial(UserRepository, User)
UserAnswersRepository = partial(UserAnswersRepository, UserDescriptiveAnswer)
ParticipantRepo = partial(ParticipantRepo, Participant)

__all__ = [
    'QuestionRepository', 'QuizRepository', 'UserRepository', 'UserAnswersRepository',
    'ParticipantRepo'
]
