from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        orm_mode: bool = True
        validate_assignment: bool = True
