from uuid import UUID

import jwt
from pwdlib import PasswordHash
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.config import config
from app.dto.user_dto import LoginRequest, LoginResponse, RegisterRequest
from app.middlewares.jwt import create_access_token, create_refresh_token
from app.models.activity import Activity
from app.models.club import Club
from app.models.user import User
from app.repositories import user_repository
from app.utils.api_response import SuccessResponse
from app.utils.errors.errors import ResponseError

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)

async def register(db: AsyncSession, payload: RegisterRequest):
    userExisting = await user_repository.get_user_by_email(db, email=payload.email)

    if userExisting:
        raise ResponseError.bad_request("Email already exist")
    
    hashed = hash_password(password= payload.password)

    user = await user_repository.register(db, name= payload.name, email= payload.email, password= hashed)

    return user

async def login(db: AsyncSession, payload: LoginRequest):
    userExisting = await user_repository.get_user_by_email(db, email=payload.email)

    if not userExisting:
        raise ResponseError.bad_request("Email or password incorrect")

    isUser = verify_password(payload.password, userExisting.password)

    if not verify_password(payload.password, userExisting.password):
        raise ResponseError.bad_request("Email or password incorrect")
    
    access_token = create_access_token({
        "id": str(userExisting.id),
        "email": userExisting.email,
        "name": userExisting.name
    })
    refresh_token = create_refresh_token({
        "id": str(userExisting.id),
        "email": userExisting.email,
        "name": userExisting.name
    })

    response = LoginResponse(
        id=userExisting.id,
        name=userExisting.name,
        email=userExisting.email,
        access_token=access_token,
        refresh_token=refresh_token
    )

    return response

async def refresh_token(db: AsyncSession,refreshToken: str):
    try:
        payload = jwt.decode(refreshToken,config.SECRET_KEY,algorithms=[config.ALGORITHM])

        if payload.get("type")!= "refresh":
            raise ResponseError.unauthorized()
        
        user_id = payload.get("id")
        userExisting = await user_repository.get_user_by_id(db, id=user_id)
        if not userExisting:
            raise ResponseError.unauthorized()
        
    except jwt.ExpiredSignatureError:
        raise ResponseError.unauthorized("Refresh token expired")

    except jwt.InvalidTokenError:
        raise ResponseError.unauthorized("Invalid token")
    
    new_access_token = create_access_token({
        "id": str(userExisting.id),
        "email": userExisting.email,
        "name": userExisting.name
    })
    new_refresh_token = create_refresh_token({
        "id": str(userExisting.id),
        "email": userExisting.email,
        "name": userExisting.name
    })

    response = LoginResponse(
        id=userExisting.id,
        name=userExisting.name,
        email=userExisting.email,
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )

async def search(db: AsyncSession, type: str, keyword: str):
    keyword = f"%{keyword.lower()}%"

    if type == "user":
        result = await db.execute(
            select(User).where(
                or_(
                    User.name.ilike(keyword),
                    User.email.ilike(keyword)
                )
            )
        )
        users = result.scalars().all()

        data = [
            {
                "id": str(u.id),
                "name": u.name,
                "email": u.email
            }
            for u in users
        ]

    elif type == "club":
        result = await db.execute(
            select(Club).where(
                Club.name.ilike(keyword),
                Club.is_deleted == False
            )
        )
        clubs = result.scalars().all()

        data = [
            {
                "id": str(c.id),
                "name": c.name,
                "is_public": c.is_public
            }
            for c in clubs
        ]

    elif type == "activity":
        result = await db.execute(
            select(Activity).where(
                Activity.name.ilike(keyword)
            )
        )
        activities = result.scalars().all()

        data = [
            {
                "id": str(a.id),
                "name": a.name,
            }
            for a in activities
        ]

    else:
        raise ResponseError.bad_request("Invalid search type")

    return SuccessResponse.response(data=data)