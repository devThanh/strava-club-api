from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_async_session
from app.services import club_service
from app.dto.club_dto import CreateClubRequest
from app.middlewares.auth_middleware import authorize

router = APIRouter(prefix="/clubs", tags=["Clubs"])

@router.post("/create")
async def create_club(
    payload: CreateClubRequest,
    db: AsyncSession = Depends(get_async_session),
    user=Depends(authorize)
):
    return await club_service.create_club(db, payload, user)


@router.get("/{club_id}/members")
async def get_members(
    club_id: str,
    db: AsyncSession = Depends(get_async_session),
):
    return await club_service.get_club_members(db, club_id)


@router.post("/{club_id}/approve/{user_id}")
async def approve_member(
    club_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(authorize)
):
    return await club_service.approve_member(db, club_id, user_id, user)

@router.post("/{club_id}/join")
async def join_club(
    club_id: str,
    db: AsyncSession = Depends(get_async_session),
    user=Depends(authorize)
):
    return await club_service.request_join(db, club_id, user)

@router.post("/{club_id}/leave")
async def leave_club(
    club_id: str,
    db: AsyncSession = Depends(get_async_session),
    user=Depends(authorize)
):
    return await club_service.leave_club(db, club_id, user)