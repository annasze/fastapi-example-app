import asyncio

import pytest
from fastapi import HTTPException, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.security.jwt import create_access_token_for_user
from app.utils.exceptions import NotAuthorizedException

pytestmark = pytest.mark.asyncio  # noqa


async def test_update_user_not_authorized(
        client: AsyncClient,
        test_db: AsyncSession,
        updated_payload_short: dict[str, str],
        test_user_credentials: dict[str, str]
):
    await User.create(test_db, **test_user_credentials)
    token = await create_access_token_for_user(username="not_authorized_user")

    response = await client.patch(
        f"/users/{test_user_credentials['username']}",
        json=updated_payload_short,
        headers=dict(token=token)
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert len(response.json()) == 1
    assert response.json()["detail"] == "Not authorized to perform requested action."


async def test_get_user_that_doesnt_exist(client: AsyncClient):
    response = await client.get(f"/users/non_existing_user")
    assert response.status_code == 404
    assert len(response.json()) == 1


async def test_login_user_invalid_credentials(
        client: AsyncClient,
        test_db: AsyncSession,
        test_user_credentials: dict[str, str],
        incorrect_test_user_credentials: dict[str, str]
):
    await User.create(test_db, **test_user_credentials)
    response = await client.post(
        "/auth/login",
        json=incorrect_test_user_credentials
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid credentials."

