from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.club import Club, ClubMember
from app.repositories import club_repository
from app.dto.club_dto import CreateClubRequest
from app.utils.api_response import SuccessResponse
from app.utils.errors.errors import ResponseError

async def create_club(db: AsyncSession, payload: CreateClubRequest, current_user):
    print(current_user)
    club = Club(
        name=payload.name,
        owner_id=current_user["id"],
        is_public=payload.is_public
    )

    club = await club_repository.create_club(db, club)

    member = ClubMember(
    user_id=current_user["id"],
    club_id=club.id,
    role="owner",
    status="approved"
)

    db.add(member)
    await db.commit()

    return SuccessResponse.response(
        data=club,
        message="Create club success"
    )


# async def join_club(db: AsyncSession, club_id, current_user):
#     club = await club_repository.get_club_by_id(db, club_id)

#     if not club:
#         raise ResponseError.bad_request("Club not found")

#     if current_user in club.members:
#         raise ResponseError.bad_request("Already joined")

#     club.members.append(current_user)
#     await db.commit()

#     return SuccessResponse.response(message="Joined club")


async def leave_club(db: AsyncSession, club_id, current_user):
    club = await club_repository.find_club_by_id(db, club_id)

    member = next(
        (m for m in club.members if str(m.id) == current_user["id"]),
        None
    )

    if not member:
        raise ResponseError.bad_request("Not a member")

    club.members.remove(member)
    await db.commit()

    return SuccessResponse.response(message="Left club")


async def get_club_members(db: AsyncSession, club_id):
    club = await club_repository.find_club_by_id(db, club_id)

    if not club:
        raise ResponseError.bad_request("Club not found")

    return SuccessResponse.response(data=[{"email":u.email, "name":u.name} for u in club.members])


async def request_join(db: AsyncSession, club_id, current_user):
    result = await db.execute(
        select(Club).where(Club.id == club_id)
    )
    club = result.scalar_one_or_none()

    if not club:
        raise ResponseError.bad_request("Club not found")

    result = await db.execute(
        select(ClubMember).where(
            ClubMember.club_id == club_id,
            ClubMember.user_id == current_user["id"]
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise ResponseError.bad_request("Already requested or joined")

    member = ClubMember(
        user_id=current_user["id"],
        club_id=club_id,
        role="member",
        status="pending"
    )

    db.add(member)
    await db.commit()

    return SuccessResponse.response(message="Request sent")

async def approve_member(
    db: AsyncSession,
    club_id,
    user_id,
    current_user
):
    result = await db.execute(
        select(Club).where(Club.id == club_id)
    )
    club = result.scalar_one_or_none()

    if not club:
        raise ResponseError.bad_request("Club not found")

    if str(club.owner_id) != str(current_user["id"]):
        raise ResponseError.unauthorized("Only owner can approve")

    result = await db.execute(
        select(ClubMember).where(
            ClubMember.club_id == club_id,
            ClubMember.user_id == user_id
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise ResponseError.bad_request("User has not requested to join")

    if member.status == "approved":
        raise ResponseError.bad_request("User already approved")

    member.status = "approved"

    await db.commit()

    return SuccessResponse.response(message="User approved")
