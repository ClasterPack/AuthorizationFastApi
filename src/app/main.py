from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.app.api.v1 import authorization
from src.core.config import Settings, settings
from src.core.logger import setup_logging
from src.infrastructure.ioc_container import SessionProvider, UowProvider


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        docs_url="/docs",
        openapi_url="/api/openapi/",
        default_response_class=ORJSONResponse,
    )
    app.include_router(authorization.router, prefix="/api/v1/user")
    return app


def app_factory():
    setup_logging()
    app = create_app()
    container = make_async_container(
        SessionProvider(),
        UowProvider(),
        context={Settings: Settings()},
    )
    setup_dishka(container=container, app=app)

    return app