
from src.app.repositories import (
    UserAnswersRepository,
    ParticipantRepo,
    QuestionRepository,
)
from src.app.schemas.extra.success import MessageResponse
from src.app.schemas.in_.user_answers import UpdateParticipantAnswersIn
from src.app.schemas.out.quizzes import (
    UserAnswersWithScoreOutList,
    ParticipantsAnswersOut,
)
from src.app.schemas.out.user_answers import ParticipantAnswersOut
from src.core.excpetions import BadRequestException
from src.core.excpetions.database import ItemNotFoundError


class UserAnswersController:
    def __init__(self, answers_repository: UserAnswersRepository):
        self.answers_repository = answers_repository

    async def update_participant_answers(
        self, participant_answers: UpdateParticipantAnswersIn
    ) -> MessageResponse:
        if participant_answers.descriptive:
            await self.update_descriptive_answers(participant_answers)

        if participant_answers.multiple_options:
            await self.answers_repository.update_multiple_option_answers(
                participant_id=participant_answers.participant_id,
                ids=participant_answers.multiple_options,
            )

        return MessageResponse(message="updated")

    async def update_descriptive_answers(
        self, participant_answers: UpdateParticipantAnswersIn
    ):
        descriptive_answer_ids: list[int] = list(
            participant_answers.descriptive.keys()
        )
        descriptive_answers = (
            await self.answers_repository.get_participant_descriptive(
                participant_id=participant_answers.participant_id,
                descriptive_ids=descriptive_answer_ids,
            )
        )
        await self.answers_repository.update_user_descriptive_answer(
            descriptive_in=participant_answers.descriptive,
            descriptive_objects=descriptive_answers,
        )

    async def get_participant_answers_with_score(
        self,
        quiz_id: int,
        participant_repo: ParticipantRepo,
        question_repository: QuestionRepository,
    ) -> ParticipantsAnswersOut:
        participants_answers = (
            await participant_repo.get_participant_answers_with_score(quiz_id=quiz_id)
        )
        quiz_score = await question_repository.total_quiz_questions_score(
            quiz_id=quiz_id
        )
        participant_answers_out = UserAnswersWithScoreOutList.validate_python(
            participants_answers
        )
        return ParticipantsAnswersOut(
            participant_answers=participant_answers_out,
            total_quiz_score=quiz_score.total_quiz_score,
        )

    async def get_participant_answers(
        self,
        quiz_id: int,
        participant_id: int,
        participant_repo: ParticipantRepo,
    ) -> ParticipantAnswersOut:
        try:
            participant_answers = await participant_repo.get_participant_with_answers(
                quiz_id=quiz_id, participant_id=participant_id
            )
        except ItemNotFoundError:
            raise BadRequestException("participant not found", "participant_not_found")

        return ParticipantAnswersOut.model_validate(participant_answers)
