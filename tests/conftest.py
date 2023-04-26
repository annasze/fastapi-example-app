import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.database import get_db
from app.main import app
from app.models.base import Base
from app.settings import settings
from tests.overwritten_db import engine, async_session_for_testing, get_db_for_testing


@pytest_asyncio.fixture(autouse=True)
async def setup_teardown():
    app.dependency_overrides[get_db] = get_db_for_testing

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


@pytest_asyncio.fixture()
async def client():
    async with AsyncClient(
            app=app,
            base_url=settings.url_for_tests,
    ) as client:
        yield client


@pytest_asyncio.fixture()
async def test_db():
    db = async_session_for_testing()
    try:
        yield db
    finally:
        await db.close()


@pytest.fixture(params=(dict(username="test", email="test@email.com", password="test"),))
def test_user_credentials(request):
    return request.param


@pytest.fixture(
    params=(
            dict(username="test", password="incorrect_password"),
            dict(email="test@email.com", password="incorrect_password"),
    )
)
def incorrect_test_user_credentials(request):
    return request.param


@pytest.fixture(
    params=(
            dict(email="updated.email@email.com"),
            dict(password="qwerty123"),
            dict(bio="Updated bio"),
            dict(image="http://img.myimage.jpg"),
            dict(password="qwerty123", email="updated.email@email.com"),
            dict(bio="Updated bio", image="http://img.myimage.jpg", password="qwerty123"),
            dict(bio="Updated bio", image="http://img.myimage.jpg", password="qwerty123",
                 email="updated.email@email.com")
    )
)
def updated_payload(request):
    return request.param


@pytest.fixture(
    params=(
            dict(email="updated.email@email.com"),
            dict(password="qwerty123"),
    )
)
def updated_payload_short(request):
    return request.param
