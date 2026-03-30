from fastapi import APIRouter, Depends, File, UploadFile, requests
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.config import config
from app.database.database import get_async_session
from app.models.activity import Activity
from app.services import club_activity_service
from app.dto.challenge_activity import CreateChallengeRequest, UpdateActivityRequest
from app.middlewares.auth_middleware import authorize
from app.utils.api_response import SuccessResponse


router = APIRouter(prefix="/challenge", tags=["Challenge"])

@router.post("/create/{club_id}")
async def create_challenge(
    payload: CreateChallengeRequest,
    club_id: str,
    db: AsyncSession = Depends(get_async_session),
    user=Depends(authorize)
):
    return await club_activity_service.create_challenge(db, club_id, payload, user)

@router.get("/{club_id}")
async def get_challenge(
    club_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    return await club_activity_service.show_challenge(db, club_id)


@router.get("/{challenge_id}/members")
async def get_members(
    challenge_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    return await club_activity_service.show_members_in_challenge(db, challenge_id)


@router.get("/activities/{challenge_id}")
async def get_all_activities(
    challenge_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    return await club_activity_service.show_all_activities(db, challenge_id)


@router.get("/activities/{activity_id}")
async def get_activity(
    activity_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    return await club_activity_service.show_activity(db, activity_id)

@router.post("/{challenge_id}/join")
async def join_challenge(
    challenge_id: str,
    db: AsyncSession = Depends(get_async_session),
    user=Depends(authorize)
):
    return await club_activity_service.join_challenge(db, challenge_id, user)


@router.delete("/{challenge_id}")
async def delete_challenge(
    challenge_id: str,
    db: AsyncSession = Depends(get_async_session),
    user = Depends(authorize)
):
    return await club_activity_service.delete_challenge(db, challenge_id, user)

@router.post("/upload/{club_id}/{challenge_id}")
async def upload_activity(
    club_id: str,
    challenge_id: str | None = None,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_session),
    user=Depends(authorize)
):
    return await club_activity_service.upload_activity(
        db, file, club_id, challenge_id, user
    )


@router.put("/{activity_id}")
async def update_activity(
    activity_id: str,
    payload: UpdateActivityRequest,
    db: AsyncSession = Depends(get_async_session),
    user=Depends(authorize)
):
    return await club_activity_service.update_activity(
        db, activity_id, payload, user
    )