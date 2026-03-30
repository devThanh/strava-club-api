import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.config.config import config
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.errors.errors import ResponseError

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def register(db: AsyncSession, name: str, email: str, password: str):
    user = User(name=name, email=email, password=password)

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user

async def get_user_by_id(db: AsyncSession, id: str):
    result = await db.execute(
        select(User).where(User.id == id)
    )
    return result.scalar_one_or_none()