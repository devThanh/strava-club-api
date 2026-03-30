from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_async_session
from app.dto.user_dto import LoginRequest, LoginResponse, RegisterRequest, UserResponse
from app.services import user_service
from app.utils.api_response import SuccessResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register")
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_async_session),
):
    user = await user_service.register(db, payload)
    return SuccessResponse.response(
        data=UserResponse.model_validate(user)
    )

@router.post("/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_async_session))->LoginResponse:
    user = await user_service.login(db, payload)
    return SuccessResponse.response(
        data=user,
        message= "Login Successfully"
    )


@router.get("")
async def search_api(
    type: str = Query(..., description="user | club | activity"),
    keyword: str = Query(...),
    db: AsyncSession = Depends(get_async_session),
):
    return await user_service.search(db, type, keyword)