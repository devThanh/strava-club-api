from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.activity import Activity
from app.models.challenge import Challenge, ChallengeMember

async def create_challenge(db: AsyncSession, challenge: Challenge):
    db.add(challenge)
    await db.commit()
    await db.refresh(challenge)
    return challenge

async def get_challenge_by_club(db: AsyncSession, club_id: str):
    result = await db.execute(
        select(Challenge)
        .where(Challenge.club_id == club_id)
        .options(
            selectinload(Challenge.members),
            selectinload(Challenge.activities)
        )
    )
    return result.scalar_one_or_none()

async def get_challenge_by_challenge_id(db: AsyncSession, challenge_id: str):
    result = await db.execute(
        select(Challenge)
        .where(Challenge.id == challenge_id)
        .options(
            selectinload(Challenge.members),
            selectinload(Challenge.activities)
        )
    )
    return result.scalar_one_or_none()

async def get_all_activities(db: AsyncSession, challenge_id: str):
    result = await db.execute(
        select(Activity)
        .where(Activity.challenge_id == challenge_id)
        .options(
            selectinload(Activity.user),
            selectinload(Activity.challenge)
        )
    )
    return result.scalars().all()

async def get_activity_by_id(db: AsyncSession, activity_id: str):
    result = await db.execute(
        select(Activity)
        .where(Activity.id == activity_id)
        .options(
            selectinload(Activity.user),
            selectinload(Activity.challenge)
        )
    )
    return result.scalar_one_or_none()

async def delete_challenge(db: AsyncSession, challenge: Challenge):
    challenge.is_deleted = True
    await db.commit()


