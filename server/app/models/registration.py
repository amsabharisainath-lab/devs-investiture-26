from datetime import datetime
from typing import Optional,List,TYPE_CHECKING
from sqlalchemy import BigInteger,Integer, ForeignKey, Enum, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.qr_token import QRToken
    from app.models.user import User
    from app.models.attendance import Attendance
    from app.models.scan_event import ScanEvent
    from app.models.od_document import ODDocument

# Assuming your declarative base is imported from core
from app.db.session import Base
from app.enum.registration_status import RegistrationStatus
from app.enum.registration_source import RegistrationSource

class Registration(Base):
    __tablename__ = "registrations"
    ID_TYPE = BigInteger().with_variant(Integer, "sqlite")

    # Primary Key
    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)

    # Foreign Keys
    event_id: Mapped[int] = mapped_column(
        ID_TYPE, ForeignKey("events.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ID_TYPE, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    
    # Registration Details
    status: Mapped[RegistrationStatus] = mapped_column(
        Enum(RegistrationStatus), nullable=False, default=RegistrationStatus.CONFIRMED
    )
    registration_source: Mapped[RegistrationSource] = mapped_column(
        Enum(RegistrationSource), nullable=False, default=RegistrationSource.SELF
    )
    
    # Admin who performed on-spot registration (Nullable)
    registered_by: Mapped[Optional[int]] = mapped_column(
        ID_TYPE, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Timestamps
    registered_at: Mapped[datetime] = mapped_column(
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
        UniqueConstraint(
            "event_id", "user_id", 
            name="uq_event_user_registration"
        ),
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------
    
    # Link back to the Event
    event: Mapped["Event"] = relationship(
        "Event", back_populates="registrations"
    )

    qr_tokens: Mapped[List["QRToken"]] = relationship(
        "QRToken", back_populates="registration"
    )
    
    # Link back to the User (Student)
    user: Mapped["User"] = relationship(
        "User", 
        foreign_keys=[user_id], 
        back_populates="registrations"
    )
    
    # Link back to the Admin who registered the user on-spot
    # Registration
    admin_registrar: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[registered_by],
        back_populates="on_spot_registrations"
    )

    attendance: Mapped[Optional["Attendance"]] = relationship(
        "Attendance",
        back_populates="registration",
        uselist=False
    )

    scan_events: Mapped[List["ScanEvent"]] = relationship(
        "ScanEvent",
        back_populates="registration"
    )

    od_documents: Mapped[List["ODDocument"]] = relationship(
        "ODDocument",
        back_populates="registration"
    )

    onspot_record: Mapped["OnSpotRegistration | None"] = relationship(
        "OnSpotRegistration", back_populates="registration", uselist=False
    )