from datetime import datetime, timezone, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.security.password import verify_password

pytestmark = pytest.mark.asyncio


async def test_create(test_db: AsyncSession, test_user_credentials: dict[str, str]):
    user = await User.create(test_db, **test_user_credentials)
    assert isinstance(user, User)
    assert isinstance(user.id, int)
    assert user.username == test_user_credentials["username"]
    assert user.email == test_user_credentials["email"]
    dts = [datetime.now(timezone.utc) - timedelta(minutes=1), datetime.now(timezone.utc)]
    assert dts[1] > user.created_at > dts[0]
    assert dts[1] > user.last_login_at > dts[0]
    assert user.hashed_password.startswith("$2b$")
    assert user.password_salt.startswith("$2b$")

    # check whether the data has been added to the db
    user_in_db = await User.find_one(test_db, "username", test_user_credentials["username"])
    assert user_in_db == user


async def test_update(test_db: AsyncSession, test_user_credentials: dict[str, str], updated_payload: dict[str, str]):
    user = await User.create(test_db, **test_user_credentials)
    await user.update(test_db, **updated_payload)

    for elem in updated_payload:
        if elem == "password":
            assert await verify_password(
                password_salt=user.password_salt,
                plain_password=updated_payload[elem],
                hashed_password=user.hashed_password
            )
        else:
            assert updated_payload[elem] == getattr(user, elem)

    updated_user_in_db = await User.find_one(test_db, "username", test_user_credentials["username"])
    assert updated_user_in_db == user


async def test_save(test_db: AsyncSession):
    user = User()
    payload = dict(
        id=111,
        username="newuser",
        email='email@email.com',
        hashed_password="notreallyhashed",
        password_salt="salt",
        created_at=datetime.now(timezone.utc),
        last_login_at=datetime.now(timezone.utc)
    )
    [setattr(user, attr, payload[attr]) for attr in payload]
    await user.save(test_db)

    user_in_db = await User.find_one(test_db, "username", payload["username"])
    assert user_in_db == user


async def test_delete(test_db: AsyncSession, test_user_credentials: dict[str, str]):
    await User.create(test_db, **test_user_credentials)
    user = await User.find_one(test_db, "email", test_user_credentials["email"])
    await user.delete(test_db)

    with pytest.raises(HTTPException):
        await User.find_one(test_db, "email", test_user_credentials["email"])


async def test_find_one(test_db: AsyncSession, test_user_credentials: dict[str, str]):
    await User.create(test_db, **test_user_credentials)
    assert await User.find_one(test_db, "email", test_user_credentials["email"])


async def test_is_taken(test_db: AsyncSession, test_user_credentials: dict[str, str]):
    await User.create(test_db, **test_user_credentials)
    assert await User.is_taken(test_db, "username", test_user_credentials["username"])
    assert await User.is_taken(test_db, "email", test_user_credentials["email"])
    assert not await User.is_taken(test_db, "username", "available_username")
    assert not await User.is_taken(test_db, "email", "available_email")


async def test_update_last_login_at(test_db: AsyncSession, test_user_credentials: dict[str, str]):
    user = await User.create(test_db, **test_user_credentials)
    last_login_at = user.last_login_at
    await user.update_last_login_at(test_db)
    assert last_login_at < user.last_login_at

