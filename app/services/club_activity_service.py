from uuid import UUID

from fastapi import requests
import httpx
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.config import config
from app.models.activity import Activity
from app.models.challenge import Challenge, ChallengeMember
from app.models.club import Club, ClubMember
from app.repositories import activity_club_repository
from app.dto.challenge_activity import CreateChallengeRequest, UpdateActivityRequest, UploadActivityResponse
from app.utils.api_response import SuccessResponse
from app.utils.errors.errors import ResponseError
from app.utils.errors.errors import ResponseError
from app.utils.image_kit import imagekit
from app.utils.util import normalize_ocr_data, parse_activity, parse_strava_text

async def create_challenge(db: AsyncSession, club_id: str, payload: CreateChallengeRequest, current_user):
    challenge = Challenge(
        name = payload.name,
        club_id = club_id
    )

    challenge_member = ChallengeMember(
        user_id = current_user["id"],
        challenge_id = challenge.id
    )

    return await activity_club_repository.create_challenge(db, challenge)

async def show_challenge(db: AsyncSession, club_id: str):
    challenge = await activity_club_repository.get_challenge_by_club(db, club_id)

    if not challenge:
        raise ResponseError.bad_request("Challenge not found")

    return SuccessResponse.response(data=challenge)

async def show_members_in_challenge(db: AsyncSession, challenge_id: str):
    challenge = await activity_club_repository.get_challenge_by_challenge_id(db, challenge_id)

    if not challenge:
        raise ResponseError.bad_request("Challenge not found")

    return SuccessResponse.response(data=challenge.members)

async def show_all_activities(db: AsyncSession, challenge_id: str):
    activities = await activity_club_repository.get_all_activities(db, challenge_id)

    return SuccessResponse.response(data=activities)

async def show_activity(db: AsyncSession, activity_id: str):
    activity = await activity_club_repository.get_activity_by_id(db, activity_id)

    if not activity:
        raise ResponseError.bad_request("Activity not found")

    return SuccessResponse.response(data=activity)

async def delete_challenge(db: AsyncSession, challenge_id: str, current_user):
    challenge = await activity_club_repository.get_challenge_by_id(db, challenge_id)

    if not challenge:
        raise ResponseError.bad_request("Challenge not found")

    if str(challenge.owner_id) != str(current_user.id):
        raise ResponseError.unauthorized("Not owner")

    await activity_club_repository.delete_challenge(db, challenge)

    return SuccessResponse.response(message="Delete challenge success")


async def upload_to_imagekit(file):
    url = "https://upload.imagekit.io/api/v1/files/upload"

    files = {
        "file": (file.filename, await file.read()),
    }

    data = {
        "fileName": file.filename,
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(
            url,
            data=data,
            files=files,
            auth=(config.IMAGEKIT_PRIVATE_KEY, "")
        )

    result = res.json()
    return result["url"]

async def call_ocr_api(image_url: str):
    payload = {
        "url": image_url,
        "isOverlayRequired": False,
        "apikey": config.OCR_API_KEY,
        "language": "eng",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.ocr.space/parse/image",
                data=payload,
            )

        data = response.json()

        if data.get("IsErroredOnProcessing"):
            raise ResponseError.bad_request("OCR failed")

        parsed_text = data["ParsedResults"][0]["ParsedText"]

        print("OCR TEXT:", parsed_text)
        raw_data = parse_strava_text(parsed_text)

        return normalize_ocr_data(raw_data)

    except httpx.ConnectError:
        raise ResponseError.bad_request("Cannot connect to OCR API")

    except Exception as e:
        raise ResponseError.bad_request(f"OCR error: {str(e)}")

async def upload_activity(db, file, club_id, challenge_id, current_user):
    result = await db.execute(
        select(ClubMember).where(
            ClubMember.club_id == club_id,
            ClubMember.user_id == current_user["id"],
            ClubMember.status == "approved"
        )
    )

    if not result.first():
        raise ResponseError.unauthorized("Not a club member")

    image_url = await upload_to_imagekit(file)

    try:
        ocr_data = await call_ocr_api(image_url)
    except:
        ocr_data = {}

    activity = Activity(
        user_id=current_user["id"],
        club_id=club_id,
        challenge_id=challenge_id,
        image_url=image_url,

        full_name=ocr_data.get("full_name"),
        activity_name=ocr_data.get("activity_name"),
        distance=ocr_data.get("distance"),
        pace=ocr_data.get("pace"),
        duration=ocr_data.get("duration"),
        activity_date=ocr_data.get("activity_date"),
    )

    db.add(activity)
    await db.commit()
    await db.refresh(activity)

    return SuccessResponse.response(
        data={
            "id": str(activity.id),
            "distance": activity.distance,
            "pace": activity.pace,
            "duration": activity.duration
        },
        message="Upload activity success"
    )


async def update_activity(db: AsyncSession, activity_id: UUID, payload, current_user: dict):
    result = await db.execute(select(Activity).where(Activity.id == activity_id))
    activity = result.scalar_one_or_none()

    if not activity:
        raise ResponseError.bad_request("Activity not found")

    result = await db.execute(select(Club).where(Club.id == activity.club_id))
    club = result.scalar_one()
    if club.owner_id != UUID(current_user["id"]):
        raise ResponseError.unauthorized("Unauthorized")

    update_data = payload.model_dump(exclude_none=True)

    if "activity_date" in update_data and update_data["activity_date"]:
        if update_data["activity_date"].tzinfo is not None:
            update_data["activity_date"] = update_data["activity_date"].replace(tzinfo=None)

    for key, value in update_data.items():
        setattr(activity, key, value)

    await db.commit()
    await db.refresh(activity)

    return UploadActivityResponse.model_validate(activity)

async def join_challenge(db: AsyncSession, challenge_id: str, current_user):
    result = await db.execute(
        select(Challenge).where(Challenge.id == challenge_id)
    )
    challenge = result.scalar_one_or_none()

    if not challenge:
        raise ResponseError.bad_request("Challenge not found")

    result = await db.execute(
        select(ClubMember).where(
            ClubMember.club_id == challenge.club_id,
            ClubMember.user_id == current_user["id"],
            ClubMember.status == "approved"
        )
    )

    if not result.first():
        raise ResponseError.unauthorized("You are not a club member")
    
    result = await db.execute(
        select(ChallengeMember).where(
            ChallengeMember.challenge_id == challenge_id,
            ChallengeMember.user_id == current_user["id"]
        )
    )

    if result.first():
        raise ResponseError.bad_request("Already joined challenge")

    await db.execute(
        insert(ChallengeMember).values(
            user_id=current_user["id"],
            challenge_id=challenge_id,
            # status="joined"
        )
    )

    await db.commit()

    return SuccessResponse.response(message="Joined challenge successfully")