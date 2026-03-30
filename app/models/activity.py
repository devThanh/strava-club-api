import uuid
from sqlalchemy import Column, Float, ForeignKey, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.database import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("challenges.id"), nullable=True)
    image_url = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    activity_name = Column(String, nullable=True)
    distance = Column(Float, nullable=True)
    pace = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    activity_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    club = relationship("Club")
    challenge = relationship("Challenge")