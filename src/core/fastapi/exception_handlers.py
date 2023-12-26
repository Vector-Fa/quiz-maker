from fastapi.requests import Request
from fastapi.responses import JSONResponse

from src.core.excpetions.http_exceptions import (
    CustomHttpException,
    UnProcessableEntityException,
)


def http_exception_handler(_: Request, exc: CustomHttpException):
    return JSONResponse(
        {
            "detail": [
                {"message": exc.message, "type": exc.type_, "loc": ["code", "manuall"]}
            ]
        },
        status_code=exc.code,
    )


def unprocessable_entity_exception(_: Request, exc: UnProcessableEntityException):
    return JSONResponse({"detail": exc.message}, status_code=exc.code)
