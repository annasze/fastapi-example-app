from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserPublic, UserInUpdate, UserInDelete, UserInDB
from app.security.jwt import decode_token
from app.utils.exceptions import NotAuthorizedException

router = APIRouter()


@router.get(
    "/{username}",
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
)
async def get_user(
        *,
        db_session: AsyncSession = Depends(get_db),
        username: str
) -> UserPublic:

    return await User.find_one(db_session, "username", username)


@router.patch(
    "/{username}",
    status_code=status.HTTP_200_OK,
    response_model=UserInDB,
)
async def update_user(
        *,
        db_session: AsyncSession = Depends(get_db),
        to_update: UserInUpdate,
        token: str = Header(),
        username: str
) -> UserInDB:

    token = await decode_token(token)
    if token.username != username:
        raise NotAuthorizedException
    instance = await User.find_one(db_session, "username", username)
    await instance.update(db_session, **to_update.dict())

    return instance


@router.delete(
    "/{username}",
    status_code=status.HTTP_200_OK,
    response_model=UserInDelete,
)
async def delete_user(
        *,
        db_session: AsyncSession = Depends(get_db),
        token: str = Header(),
        username: str
) -> UserInDelete:

    token = await decode_token(token)
    if token.username != username:
        raise NotAuthorizedException
    instance = await User.find_one(db_session, "username", username)
    await instance.delete(db_session)

    return UserInDelete(deleted_user=instance)
