from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserInCreate, UserPublic, UserInLogin, UserWithToken
from app.security.jwt import create_access_token_for_user
from app.security.user import verify_user

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublic
)
async def register_user(
        *,
        db_session: AsyncSession = Depends(get_db),
        user_data: UserInCreate
) -> UserPublic:

    return await User.create(db_session, **user_data.dict())


@router.post(
    "/login",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=UserWithToken
)
async def login_user(
        *,
        db_session: AsyncSession = Depends(get_db),
        credentials: UserInLogin
) -> UserWithToken:

    user = await verify_user(db_session, credentials)
    token = await create_access_token_for_user(credentials.username)
    await user.update_last_login_at(db_session)

    return UserWithToken(user=user, token=token)
