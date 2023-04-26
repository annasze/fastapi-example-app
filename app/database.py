from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.settings import settings


engine = create_async_engine(settings.asyncpg_url)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False
)


async def get_db():
    db = async_session()
    try:
        yield db
    finally:
        await db.close()


