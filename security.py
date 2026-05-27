# security.py file, contains data for passwords and tokens

from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, UTC
from config import settings as stngs

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_toker(data: dict) ->str:
    expire = datetime.now(UTC) + timedelta(minutes=stngs.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({**data, "exp":expire}, stngs.JWT_SECRET_KEY, stngs.JWT_ALGORITHM)

def create_refresh_token(data: dict) ->str:
    expire = datetime.now(UTC) + timedelta(days = stngs.REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode({**data, "exp":expire, "type": "refresh"}, stngs.JWT_SECRET_KEY, stngs.JWT_ALGORITHM)

def decode_token(token:str) -> dict:
    return jwt.decode(token, stngs.JWT_SECRET_KEY, algorithms=[stngs.JWT_ALGORITHM])