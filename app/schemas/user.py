from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from pydantic import EmailStr, HttpUrl, root_validator

from app.schemas.base import BaseSchema


class UserBase(BaseSchema):
    username: str
    email: EmailStr


class UserInCreate(UserBase):
    password: str


class UserInLogin(BaseSchema):
    # allow logging in either with username or email
    username: Optional[str]
    email: Optional[str]
    password: str

    @root_validator(pre=True)
    def check_credentials(cls, values):    # noqa
        if not values.get("username") and not values.get("email"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either username or email must be provided."
            )
        return values


class UserInUpdate(BaseSchema):
    email: Optional[EmailStr]
    bio: Optional[str]
    image: Optional[HttpUrl]
    password: Optional[str]


class UserInDB(UserBase):
    id: int
    bio: Optional[str]
    image: Optional[HttpUrl]
    created_at: datetime
    last_login_at: datetime


class UserPublic(BaseSchema):
    username: str
    bio: Optional[str]
    image: Optional[HttpUrl]
    created_at: datetime
    last_login_at: datetime


class UserWithToken(BaseSchema):
    token: str
    user: UserInDB


class UserInDelete(BaseSchema):
    deleted_user: UserPublic


class UserInDBForTests(UserBase):
    id: int
    bio: Optional[str]
    image: Optional[HttpUrl]
    password_salt: str
    hashed_password: str
    created_at: datetime
    last_login_at: datetime

