from datetime import datetime
from typing import List,TYPE_CHECKING
from sqlalchemy import BigInteger, String, DateTime, Enum, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
if TYPE_CHECKING:
    from app.models.registration import Registration

from app.db.session import Base
from app.enum.event_status import EventStatus

class Event(Base):
    __tablename__ = "events"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Event Details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Scheduling Timestamps
    entry_open_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exit_open_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    entry_close_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exit_close_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
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
        "entry_open_at < entry_close_at",
        name="check_entry_open_before_close"
    ),
    CheckConstraint(
        "exit_open_at < exit_close_at",
        name="check_exit_open_before_close"
    ),
    CheckConstraint(
        "entry_close_at <= exit_open_at",
        name="check_entry_before_exit"
    ),
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------
    
    # An event can have multiple registrations
    registrations: Mapped[List["Registration"]] = relationship(
        "Registration", back_populates="event"
    )