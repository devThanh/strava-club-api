

import uuid
from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Club(Base):
    __tablename__ = "clubs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    is_public = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship(
        "User",
        back_populates="owned_clubs",
        foreign_keys=[owner_id]
    )

    member_links = relationship(
        "ClubMember",
        back_populates="club",
        cascade="all, delete-orphan"
    )

    members = relationship(
        "User",
        secondary="club_members",
        back_populates="clubs",
    )

    challenges = relationship(
        "Challenge",
        back_populates="club"
    )


class ClubMember(Base):
    __tablename__ = "club_members"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id"), primary_key=True)
    role = Column(String, default="member")
    status = Column(String, default="pending")
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="club_links")
    club = relationship("Club", back_populates="member_links")