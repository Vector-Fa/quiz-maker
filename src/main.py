import uvicorn

from src.core.config import settings, Environments

if __name__ == "__main__":
    uvicorn.run(
        "src.core.server:app",
        reload=False if settings.ENVIRONMENT == Environments.PRODUCTION else True,
    )
