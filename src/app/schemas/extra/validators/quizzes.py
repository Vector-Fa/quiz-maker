from pydantic_core import PydanticCustomError
from pydantic_core.core_schema import ValidationInfo


def check_correct_option_index(cls, v, values: ValidationInfo) -> int:
    """check correct_option_index value is not greater than options lengths"""
    options = values.data.get("options", [])
    if v > len(options) - 1:
        raise PydanticCustomError(
            "correct answer index out of range", "correct_answer_index_out_of_range"
        )
    return v
