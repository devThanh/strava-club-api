


from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt

from app.config.config import config
from app.utils.errors.errors import ResponseError


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def authorize(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM],
        )

        if payload.get("type") != "access":
            raise ResponseError.unauthorized()

        return payload

    except jwt.ExpiredSignatureError:
        raise ResponseError.unauthorized("Token expired")

    except jwt.InvalidTokenError:
        raise ResponseError.unauthorized("Invalid token")