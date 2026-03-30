import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.database import Base

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    club = relationship("Club", back_populates="challenges")
    members = relationship(
        "User",
        secondary="challenge_members",
        back_populates="challenges"
    )
    activities = relationship("Activity", back_populates="challenge")

class ChallengeMember(Base):
    __tablename__ = "challenge_members"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("challenges.id"), primary_key=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
