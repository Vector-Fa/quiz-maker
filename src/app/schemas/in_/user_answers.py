from pydantic import BaseModel, PositiveInt


# ====-----====
class UserDescriptiveAnswersIn(BaseModel):
    score: float


class UpdateParticipantAnswersIn(BaseModel):
    participant_id: PositiveInt
    descriptive: dict[PositiveInt, UserDescriptiveAnswersIn]
    multiple_options: list[PositiveInt]


# ====-----====
