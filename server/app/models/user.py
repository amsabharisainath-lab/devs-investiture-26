from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import BigInteger, String, SmallInteger, Boolean, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.registration import Registration
    from app.models.audit_event import AuditEvent
    from app.models.scan_event import ScanEvent
    from app.models.attendance import Attendance
    from app.models.station import Station

from app.db.session import Base
from app.enum.user_role import UserRole


class User(Base):
    __tablename__ = "users"

    # Primary Key
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    # Identifiers & Contact
    # Turn this to nullable and Mapped[Optional[str]]
    google_sub: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Student Specific (Nullable)
    roll_no: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    department: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    year: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True
    )

    # Authorization & Status
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.STUDENT
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------

    # A user can have multiple registrations
    registrations: Mapped[List["Registration"]] = relationship(
        "Registration",
        back_populates="user",
        foreign_keys="Registration.user_id"
    )

    # Registrations created on behalf of users
    on_spot_registrations: Mapped[List["Registration"]] = relationship(
        "Registration",
        foreign_keys="Registration.registered_by",
        back_populates="admin_registrar"
    )

    # Audit logs triggered by this user
    # audit_events: Mapped[List["AuditEvent"]] = relationship(
    #     "AuditEvent",
    #     back_populates="actor"
    # )

    # Scans performed by this user
    scan_events: Mapped[List["ScanEvent"]] = relationship(
        "ScanEvent",
        back_populates="actor"
    )

    # Attendance records verified by this user
    verified_attendances: Mapped[List["Attendance"]] = relationship(
        "Attendance",
        foreign_keys="Attendance.verified_by",
        back_populates="verifier"
    )

    # Stations assigned to this admin/checker
    assigned_stations: Mapped[List["Station"]] = relationship(
        "Station",
        back_populates="assigned_admin"
    )

    # Add this relationship so User -> its (optional) on-spot record is reachable
    onspot_registration: Mapped["OnSpotRegistration | None"] = relationship(
        "OnSpotRegistration",
        foreign_keys="OnSpotRegistration.user_id",
        back_populates="user",
        uselist=False,
    )