from src.core.excpetions import ForbiddenException


async def access_control(policies: tuple, **kwargs) -> None:
    """
    iterate over policies in order they are given, and check if one of them is true
    user can proceed the request
    """
    for policy in policies:
        result = await policy(kwargs)
        if result:
            return
    raise ForbiddenException("access denied", "access_denied")
