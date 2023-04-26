from datetime import datetime, timezone
from typing import Optional, Self  # noqa

from fastapi import HTTPException, status
from sqlalchemy import Integer, String, TIMESTAMP, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.security.password import generate_salt, get_password_hash


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    bio: Mapped[Optional[str]]
    image: Mapped[Optional[str]]
    hashed_password: Mapped[str]
    password_salt: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    last_login_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # posts: Mapped[list["Post"]] = relationship()
    # comments: Mapped[list["Comment"]] = relationship()

    async def update(self, db_session: AsyncSession, **kwargs):
        if kwargs.get("password"):
            self.password_salt = await generate_salt()
            self.hashed_password = await get_password_hash(
                password_salt=self.password_salt,
                plain_password=kwargs["password"]
            )
        await super().update(db_session, **kwargs)

    @classmethod
    async def check_credentials_for_create(cls, db_session: AsyncSession, **kwargs) -> None:
        if await cls.is_taken(db_session, "email", kwargs["email"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'{kwargs["email"]} already exist in the database.'
            )
        if await cls.is_taken(db_session, "username", kwargs["username"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'{kwargs["username"]} is already taken.'
            )

    @classmethod
    async def create(cls, db_session: AsyncSession, **kwargs) -> Self:

        try:
            await cls.check_credentials_for_create(db_session, **kwargs)
            instance = User()
            await instance.update(db_session, **kwargs)
            await instance.save(db_session)
            return instance

        except SQLAlchemyError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=repr(exc)
            ) from exc

    async def update_last_login_at(self, db_session: AsyncSession):
        return await super().update(db_session, **{"last_login_at": datetime.now(timezone.utc)})

