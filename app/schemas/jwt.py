import datetime

from app.schemas.base import BaseSchema


class JWToken(BaseSchema):
    username: str
    exp: datetime.datetime

