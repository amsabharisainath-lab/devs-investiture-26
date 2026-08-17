from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, String, SmallInteger, Boolean, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.enum.user_role import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    google_sub: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    roll_no: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )