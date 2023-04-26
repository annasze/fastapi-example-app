import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn

load_dotenv()


class Settings(BaseSettings):
    asyncpg_url: PostgresDsn = PostgresDsn.build(
        scheme="postgresql+asyncpg",
        user=os.getenv("SQL_USER"),
        password=os.getenv("SQL_PASS"),
        host=os.getenv("SQL_HOST"),
        port=os.getenv("SQL_PORT"),
        path=f"/{os.getenv('SQL_DB')}"
    )
    asyncpg_url_for_tests = asyncpg_url.replace(os.getenv('SQL_DB'), os.getenv('SQL_TEST_DB'))
    url_for_tests = os.getenv('ALLOWED_HOST_2')
    allowed_hosts = [os.getenv('ALLOWED_HOST_1'), os.getenv('ALLOWED_HOST_2')]

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    ALGORITHM: str = os.getenv("ALGORITHM")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
