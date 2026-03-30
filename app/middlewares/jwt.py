import jwt
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash

from app.config.config import config

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = config.REFRESH_TOKEN_EXPIRE_DAYS

def create_access_token(data: dict):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])