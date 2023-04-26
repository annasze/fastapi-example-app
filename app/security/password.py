import bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def generate_salt() -> str:
    return bcrypt.gensalt().decode()


async def get_password_hash(password_salt: str, plain_password: str) -> str:
    return pwd_context.hash(password_salt + plain_password)


async def verify_password(password_salt: str, plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password_salt + plain_password, hashed_password)
