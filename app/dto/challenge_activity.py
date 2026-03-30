from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID
from datetime import datetime

class CreateChallengeRequest(BaseModel):
    name: str





class UploadActivityResponse(BaseModel):
    id: UUID
    image_url: str
    full_name: str | None
    activity_name: str | None
    distance: float | None
    pace: str | None
    duration: str | None
    activity_date: datetime | None


class UpdateActivityRequest(BaseModel):
    full_name: Optional[str] = None
    activity_name: Optional[str] = None
    distance: Optional[float] = None
    pace: Optional[str] = None
    duration: Optional[str] = None
    activity_date: Optional[datetime] = None

    @field_validator("activity_date")
    @classmethod
    def make_naive(cls, v: datetime):
        if v is not None and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v
    

class UploadActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    activity_name: str
    distance: float
    pace: str
    duration: str
    activity_date: datetime