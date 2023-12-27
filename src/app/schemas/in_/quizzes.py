from typing import Annotated

from pydantic_core import PydanticCustomError
from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    field_validator,
    model_validator,
    NonNegativeInt,
    StringConstraints,
)

from src.app.schemas.extra.validators.quizzes import check_correct_option_index
from src.app.schemas.types import Slug, UTCDateTime


# ==========--------- quiz creation ---------==========
class CreateQuizIn(BaseModel):
    title: Annotated[str, StringConstraints(min_length=3, max_length=200)]


# ====-----====
class AddShortDescriptiveQuestionIn(BaseModel):
    question: Annotated[str, StringConstraints(max_length=355)]
    answer: Annotated[str | None, StringConstraints(max_length=355)] = None
    score: float
    quiz_id: PositiveInt


class AddLongDescriptiveQuestionIn(BaseModel):
    question: Annotated[str, StringConstraints(max_length=355)]
    answer: Annotated[str | None, StringConstraints(max_length=600)] = None
    score: float
    quiz_id: PositiveInt


# ====-----====


class MultipleOptionIn(BaseModel):
    text: str


class AddMultipleOptionQuestionIn(BaseModel):
    question: str
    quiz_id: PositiveInt
    options: list[MultipleOptionIn] = Field(..., min_length=2)
    score: float = 1
    correct_option_index: NonNegativeInt

    _validator = field_validator("correct_option_index")(check_correct_option_index)  # noqa


# ====-----====
class QuizPasswordIn(BaseModel):
    password: str
    quiz_lock: bool


# ====-----====


class QuizSettingIn(BaseModel):
    title: str | None = None
    start_at: UTCDateTime | None = None
    end_at: UTCDateTime | None = None
    quiz_path: Slug | None = Field(None, min_length=7, max_length=30)
    shuffle_options: bool | None = None

    @model_validator(mode="after")
    def validate_start_is_before_end(self):
        """
        check if both dates are present, validate them
        if not, set dates to None to ignore them when updating quiz settings
        for consistent date times in database
        """
        if self.start_at and self.end_at:
            if self.start_at > self.end_at:
                raise PydanticCustomError(
                    "start_date_is_after_end", "start date is invalid"
                )
        else:
            self.start_at, self.end_at = None, None

        return self


# ====-----====
class UpdateDescriptiveQuestionIn(BaseModel):
    text: Annotated[str, StringConstraints(max_length=355)]
    new_score: float
    answer: Annotated[str | None, StringConstraints(max_length=355)] = None


# ====-----====
class MultipleOptionUpdateIn(BaseModel):
    id: PositiveInt | None = None
    text: str


class UpdateMultipleOptionQuestionIn(BaseModel):
    text: Annotated[str, StringConstraints(max_length=355)]
    options: list[MultipleOptionUpdateIn] = Field(..., min_length=2)
    new_score: float
    correct_option_index: NonNegativeInt

    _validator = field_validator("correct_option_index")(check_correct_option_index)  # noqa


# ====-----====


class UserDescriptiveAnswersIn(BaseModel):
    question_id: PositiveInt
    answer: Annotated[str, StringConstraints(max_length=600)]


class UserMultipleOptionAnswersIn(BaseModel):
    question_id: PositiveInt
    option_id: PositiveInt


class ParticipantInfoIn(BaseModel):
    username: Annotated[str, StringConstraints(max_length=355)]

    @field_validator("username")
    def validate_username_character(cls, v):
        if "+" in v:
            raise PydanticCustomError(
                "bad_username_character", 'username must not include "+" character'
            )
        return v


class UserQuestionAnswersIn(BaseModel):
    participant_info: ParticipantInfoIn
    descriptive: list[UserDescriptiveAnswersIn]
    multiple_options: list[UserMultipleOptionAnswersIn]


# ====-----====


class QuizEnterPasswordIn(BaseModel):
    password: str | None = None
