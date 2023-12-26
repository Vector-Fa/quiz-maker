from datetime import timezone, datetime
from typing import Annotated

from pydantic import AfterValidator, StringConstraints, AwareDatetime
from pydantic_core import PydanticCustomError

from src.core.utils.slugify import slugify

Slug = Annotated[str, AfterValidator(slugify)]

StrongPassword = Annotated[
    str, StringConstraints(min_length=6, pattern=r"^.*[@$!%*?&].*$", max_length=60)
]


def date_to_utc(value):
    """change given date timezone to utc"""
    if value is not None:
        value = value.replace(tzinfo=timezone.utc).astimezone(timezone.utc)
        is_input_date_on_future = value > datetime.now(tz=timezone.utc)
        if is_input_date_on_future:
            return value
        else:
            raise PydanticCustomError(
                "datetime_must_be_in_future", "input datetime is not in the future"
            )


UTCDateTime = Annotated[AwareDatetime, AfterValidator(date_to_utc)]
