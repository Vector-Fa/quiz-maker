from pydantic import BaseModel, PositiveInt, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PositiveInt
    full_name: str
    email: str
    is_admin: bool
