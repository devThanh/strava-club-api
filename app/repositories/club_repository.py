import jwt
from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session, selectinload
from app.config.config import config
from app.models.club import Club, ClubMember
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.errors.errors import ResponseError

async def create_club(db: AsyncSession, club: Club):
    db.add(club)
    await db.commit()
    await db.refresh(club)
    return club

# async def add_member(db: AsyncSession, club_id, user: User):
#     club = await db.get(Club, club_id)

#     if not club:
#         raise ResponseError.bad_request("Club not found")
    
#     if user in club.members:
#         raise ResponseError.bad_request("User already in club")

#     club.members.append(user)

#     await db.commit()
#     return club

async def get_list_club(db: AsyncSession):
    result = await db.execute(select(Club))
    return result.scalars().all()

async def find_club_by_id(db: AsyncSession, club_id):
    result = await db.execute(
        select(Club)
        .options(selectinload(Club.members))
        .where(Club.id == club_id)
    )
    return result.scalar_one_or_none()

async def find_club_by_name(db: AsyncSession, name: str):
    result = await db.execute(
        select(Club).where(Club.name == name)
    )
    return result.scalar_one_or_none()


async def get_list_member(db: AsyncSession, club_id):
    result = await db.execute(
        select(Club)
        .options(selectinload(Club.members))
        .where(Club.id == club_id)
    )

    club = result.scalar_one_or_none()

    if not club:
        raise ResponseError.bad_request("Club not found")

    return club.members

async def soft_delete_club(db: AsyncSession, club_id):
    club = await db.get(Club, club_id)

    if not club:
        raise ResponseError.bad_request("Club not found")

    club.is_deleted = True

    await db.commit()
    return club

async def join_club(db, club_id, user_id):
    club = await db.get(Club, club_id)
    if not club:
        raise ResponseError.bad_request("Club not found")

    result = await db.execute(
        select(ClubMember).where(
            ClubMember.c.club_id == club_id,
            ClubMember.c.user_id == user_id
        )
    )
    existing = result.first()

    if existing:
        raise ResponseError.bad_request("Already requested or joined")
    
    club_member = ClubMember(
        club_id=club_id,
        user_id=user_id,
        status="pending"
    )

    db.add(club_member)
    await db.commit()
    return True


async def approve_member(db, club_id, user_id):
    await db.execute(
        update(ClubMember)
        .where(
            ClubMember.club_id == club_id,
            ClubMember.user_id == user_id
        )
        .values(status="approved")
    )

    await db.commit()
    return True


async def get_members(db, club_id):
    result = await db.execute(
        select(User)
        .join(ClubMember)
        .where(
            ClubMember.club_id == club_id,
            ClubMember.status == "approved"
        )
    )

    return result.scalars().all()

async def get_members_wait_approve(db, club_id):
    result = await db.execute(
        select(User)
        .join(ClubMember)
        .where(
            ClubMember.club_id == club_id,
            ClubMember.status == "pending"
        )
    )

    return result.scalars().all()