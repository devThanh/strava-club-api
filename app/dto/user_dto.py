from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    id: UUID
    name: str
    email: str
    access_token: str
    refresh_token: str