from datetime import datetime
from typing import List
from sqlalchemy import BigInteger, String, DateTime, Enum, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Assuming your declarative base is imported from core
from app.core.database import Base
from app.enums.event_status import EventStatus

class Event(Base):
    __tablename__ = "events"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Event Details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Scheduling Timestamps
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exit_open_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Status
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus), nullable=False, default=EventStatus.UPCOMING
    )

    # Audit Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )

    # ---------------------------------------------------------
    # Table Constraints
    # ---------------------------------------------------------
    __table_args__ = (
        CheckConstraint(
            "start_at < end_at",
            name="check_start_before_end"
        ),
        CheckConstraint(
            "start_at <= exit_open_at AND exit_open_at <= end_at",
            name="check_exit_open_within_event"
        ),
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------
    
    # An event can have multiple registrations
    registrations: Mapped[List["Registration"]] = relationship(
        "Registration", back_populates="event"
    )