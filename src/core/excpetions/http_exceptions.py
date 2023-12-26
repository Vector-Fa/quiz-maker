from http import HTTPStatus


class CustomHttpException(Exception):
    code = HTTPStatus.BAD_GATEWAY
    error_code = HTTPStatus.BAD_GATEWAY

    def __init__(self, message: str, type_: str):
        self.message = message
        self.type_ = type_


class BadRequestException(CustomHttpException):
    code = HTTPStatus.BAD_REQUEST
    error_code = HTTPStatus.BAD_REQUEST


class ForbiddenException(CustomHttpException):
    code = HTTPStatus.FORBIDDEN
    error_code = HTTPStatus.FORBIDDEN


class UnAuthorizedException(CustomHttpException):
    code = HTTPStatus.UNAUTHORIZED
    error_code = HTTPStatus.UNAUTHORIZED


class UnProcessableEntityException(Exception):
    code = HTTPStatus.UNPROCESSABLE_ENTITY

    def __init__(self, loc: list, type: str):
        self.message = [{"type": type, "loc": loc}]
