from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.settings import settings


engine = create_async_engine(settings.asyncpg_url_for_tests)

async_session_for_testing = async_sessionmaker(
    engine,
    expire_on_commit=False
)


async def get_db_for_testing():
    db = async_session_for_testing()
    try:
        yield db
    finally:
        await db.close()
