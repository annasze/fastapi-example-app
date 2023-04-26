from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserInLogin
from app.security.password import verify_password
from app.utils.exceptions import InvalidCredentialsException


async def verify_user(
        db_session: AsyncSession,
        credentials: UserInLogin
) -> User:

    if credentials.username:
        if not await User.is_taken(db_session, "username", credentials.username):
            raise InvalidCredentialsException
        user_db_data = await User.find_one(db_session, "username", credentials.username)
    else:
        if not await User.is_taken(db_session, "email", credentials.email):
            raise InvalidCredentialsException
        user_db_data = await User.find_one(db_session, "email", credentials.email)

    if not await verify_password(
            password_salt=user_db_data.password_salt,
            hashed_password=user_db_data.hashed_password,
            plain_password=credentials.password):
        raise InvalidCredentialsException

    return user_db_data
