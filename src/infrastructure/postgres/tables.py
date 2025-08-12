import uuid
from datetime import UTC, datetime, timezone

from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.infrastructure.postgres.base import Base


class UserSQL(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    login_history = relationship("LoginHistorySQL", back_populates="user")
    token_version = Column(Integer, default=0, nullable=False)


class LoginHistorySQL(Base):
    __tablename__ = "login_history"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship(UserSQL, back_populates="login_history")
    user_agent = Column(Text)
    login_date = Column(DateTime, default=datetime.now(UTC))
    extra_data = Column(JSON, nullable=True)