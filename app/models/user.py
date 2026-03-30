import datetime
import uuid

from sqlalchemy import Column, UUID, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.database.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)

    owned_clubs = relationship(
        "Club",
        back_populates="owner",
        foreign_keys="Club.owner_id"
    )

    club_links = relationship(
        "ClubMember",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    clubs = relationship(
        "Club",
        secondary="club_members",
        back_populates="members",
    )

    challenges = relationship(
        "Challenge",
        secondary="challenge_members",
        back_populates="members"
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )