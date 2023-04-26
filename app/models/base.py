from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import as_declarative

from typing import Self  # noqa


@as_declarative()
class Base:

    async def save(self, db_session: AsyncSession) -> None:

        try:
            db_session.add(self)
            await db_session.commit()
            await db_session.refresh(self)

        except SQLAlchemyError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=repr(exc)
            ) from exc

    async def update(self, db_session: AsyncSession, **kwargs) -> Self:

        for k, v in kwargs.items():
            if v and hasattr(self, k):
                setattr(self, k, v)

        await self.save(db_session)
        return self

    async def delete(self, db_session: AsyncSession) -> None:

        try:
            await db_session.delete(self)
            await db_session.commit()

        except SQLAlchemyError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=repr(exc)
            ) from exc

    @classmethod
    async def find_one(
            cls,
            db_session: AsyncSession,
            attr_name: str,
            attr_value: str
    ) -> Self:

        stmt = select(cls).where(getattr(cls, attr_name) == attr_value)
        result = await db_session.execute(stmt)
        instance = result.scalar()
        if instance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"There is no record for: {attr_value}"
            )

        return instance

    @classmethod
    async def is_taken(cls, db_session: AsyncSession, attr_name: str, attr_value: str) -> bool:
        attr = getattr(cls, attr_name)
        stmt = select(attr).where(attr == attr_value)
        if await db_session.scalar(stmt):
            return True
        return False
