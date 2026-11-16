from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for ORM models."""

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
