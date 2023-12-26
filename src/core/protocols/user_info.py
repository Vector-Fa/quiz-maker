from typing import Protocol

from pydantic import PositiveInt


class UserInfo(Protocol):
    """
    UserInfo protocol can be used to read user info from jwt token or database
    """

    user_id: PositiveInt
    is_admin: bool
