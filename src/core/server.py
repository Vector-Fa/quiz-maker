from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .fastapi.exception_handlers import (
    http_exception_handler,
    unprocessable_entity_exception,
)
from ..api import api_router
from .config import settings, Environments
from .excpetions.http_exceptions import (
    CustomHttpException,
    UnProcessableEntityException,
)


def add_routers(app_: FastAPI) -> None:
    app_.include_router(api_router)


def add_cors(app_: FastAPI):
    origins = ["*"]
    app_.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="quiz creator",
        description="api for creating quizzes",
        version="1.0.0",
        debug=False if settings.ENVIRONMENT == Environments.PRODUCTION else True,
        docs_url=None if settings.ENVIRONMENT == Environments.PRODUCTION else "/docs",
        redoc_url=None if settings.ENVIRONMENT == Environments.PRODUCTION else "/docs",
    )
    add_routers(app_)
    add_cors(app_)
    app_.add_exception_handler(CustomHttpException, http_exception_handler)
    app_.add_exception_handler(
        UnProcessableEntityException, unprocessable_entity_exception
    )
    return app_


app = create_app()
