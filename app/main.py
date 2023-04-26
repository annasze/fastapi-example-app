from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.settings import settings


def get_app() -> FastAPI:
    application = FastAPI()

    application.include_router(auth_router, prefix="/auth", tags=["Auth"])
    application.include_router(user_router, prefix="/users", tags=["User"])

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return application


app = get_app()
