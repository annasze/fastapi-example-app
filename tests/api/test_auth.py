from datetime import datetime, timezone, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserInDBForTests
from app.security.jwt import decode_token
from app.security.password import verify_password

pytestmark = pytest.mark.asyncio  # noqa


async def test_register_user(client: AsyncClient, test_db: AsyncSession, test_user_credentials: dict[str, str]):
    response = await client.post("/auth/register", json=test_user_credentials)
    assert response.status_code == 201
    # check returned data
    user_data = response.json()
    assert user_data["username"] == test_user_credentials["username"]
    assert all(value is None for value in [user_data["bio"], user_data["image"]])
    assert all(key not in user_data for key in ["password", "hashed_password", "password_salt"])
    dts = [datetime.now(timezone.utc) - timedelta(minutes=1), datetime.now(timezone.utc)]
    assert dts[1] > datetime.fromisoformat(user_data["created_at"]) > dts[0]
    assert dts[1] > datetime.fromisoformat(user_data["last_login_at"]) > dts[0]

    # check whether user has been added to db
    user_data = await User.find_one(test_db, "username", test_user_credentials["username"])
    user_data = UserInDBForTests.from_orm(user_data)
    assert user_data.username == test_user_credentials["username"]
    assert await verify_password(
        password_salt=user_data.password_salt,
        plain_password=test_user_credentials["password"],
        hashed_password=user_data.hashed_password
    )


async def test_login_user(client: AsyncClient, test_db: AsyncSession, test_user_credentials: dict[str, str]):
    await User.create(test_db, **test_user_credentials)
    response = await client.post("/auth/login", json=test_user_credentials)
    assert response.status_code == 202
    user_data = response.json()
    assert (await decode_token(user_data["token"])).username == user_data["user"]["username"]
    assert len(user_data["user"]) == 7
    assert all(key in user_data["user"] for key in
               ["id", "username", "email", "bio", "image", "created_at", "last_login_at"]
               )
