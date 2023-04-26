import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserInDBForTests
from app.security.password import verify_password
from app.security.jwt import create_access_token_for_user

pytestmark = pytest.mark.asyncio


async def test_get_user(client: AsyncClient, test_db: AsyncSession, test_user_credentials: dict[str, str]):

    await User.create(test_db, **test_user_credentials)
    response = await client.get(f"/users/{test_user_credentials['username']}")
    user_data = response.json()
    assert response.status_code == 200
    assert len(user_data) == 5
    assert user_data["username"] == test_user_credentials["username"]
    assert all(key in user_data for key in ["username", "bio", "image", "created_at", "last_login_at"])
    assert all(key not in user_data for key in ["password", "hashed_password", "password_salt"])


async def test_update_user(
        client: AsyncClient,
        test_db: AsyncSession,
        updated_payload: dict[str, str],
        test_user_credentials: dict[str, str]
):
    await User.create(test_db, **test_user_credentials)
    token = await create_access_token_for_user(test_user_credentials["username"])

    await client.patch(f"/users/{test_user_credentials['username']}", json=updated_payload, headers=dict(token=token))
    updated_user_data = await User.find_one(test_db, "username", test_user_credentials["username"])
    updated_user_data = UserInDBForTests.from_orm(updated_user_data)
    for elem in updated_payload:
        if elem == "password":
            assert await verify_password(
                password_salt=updated_user_data.password_salt,
                plain_password=updated_payload[elem],
                hashed_password=updated_user_data.hashed_password
            )
        else:
            assert updated_payload[elem] == getattr(updated_user_data, elem)


async def test_delete_user(
        client: AsyncClient,
        test_db: AsyncSession,
        test_user_credentials: dict[str, str]
):
    await User.create(test_db, **test_user_credentials)
    token = await create_access_token_for_user(test_user_credentials["username"])

    response = await client.delete(f"/users/{test_user_credentials['username']}", headers=dict(token=token))
    user_data = response.json()
    assert response.status_code == 200
    assert user_data["deleted_user"]["username"] == test_user_credentials["username"]

    # # check whether user has been deleted from the db
    with pytest.raises(HTTPException):
        await User.find_one(test_db, "username", test_user_credentials["username"])



