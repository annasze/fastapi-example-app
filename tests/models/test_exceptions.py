import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.models.user import User

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "attr_name,attr_value",
    (
            ("email", "wrong_email@email.com"),
            ("username", "non-existing_username"),
            ("id", 7777)
    )
)
async def test_find_one_non_existing_record(test_db: AsyncSession, attr_name: str, attr_value: str | int):
    with pytest.raises(HTTPException):
        await User.find_one(test_db, attr_name, attr_value)


async def test_check_credentials_for_create(test_db: AsyncEngine, test_user_credentials: dict[str, str]):
    await User.create(test_db, **test_user_credentials)

    with pytest.raises(HTTPException):
        await User.check_credentials_for_create(
            test_db,
            **dict(username=test_user_credentials["username"], email="available@email.com")
        )
    with pytest.raises(HTTPException):
        await User.check_credentials_for_create(
            test_db,
            **dict(username="available_username", email=test_user_credentials["email"])
        )



