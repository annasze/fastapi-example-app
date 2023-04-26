import datetime
from typing import Callable

from fastapi import HTTPException, status
from jose import jwt
from pydantic import ValidationError

from app.schemas.jwt import JWToken
from app.settings import settings


async def create_jwt_token(
        *,
        payload: dict[str, str],
        secret_key: str,
        expires_delta: datetime.timedelta,
) -> Callable[[...], str]:
    to_encode = payload.copy()
    if expires_delta:
        expires = datetime.datetime.utcnow() + expires_delta
    else:
        expires = datetime.datetime.utcnow() + settings.ACCESS_TOKEN_EXPIRE_MINUTES
    to_encode.update(dict(exp=expires))

    return jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)


async def create_access_token_for_user(username) -> str:
    return await create_jwt_token(
        payload=dict(username=username),
        secret_key=settings.SECRET_KEY,
        expires_delta=datetime.timedelta(
            minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    )


async def decode_token(token: str) -> JWToken:
    try:
        return JWToken(
            **jwt.decode(
                token=token,
                key=settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your token has expired."
        )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to decode JWT token."
        )
