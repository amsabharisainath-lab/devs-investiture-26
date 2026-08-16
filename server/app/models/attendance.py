from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, ForeignKey, Enum, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Assuming your declarative base is imported from core
from app.core.database import Base
from app.enums.attendance_status import AttendanceStatus, AttendanceDecision

class Attendance(Base):
    __tablename__ = "attendance"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign Keys
    registration_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("registrations.id", ondelete="RESTRICT"), 
        unique=True,      # Enforces 1 registration = 1 attendance record
        nullable=False
    )
    
    # State tracking
    entry_status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus), nullable=False, default=AttendanceStatus.PENDING
    )
    exit_status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus), nullable=False, default=AttendanceStatus.PENDING
    )
    
    # Manual Verification / Decision
    decision: Mapped[Optional[AttendanceDecision]] = mapped_column(
        Enum(AttendanceDecision), nullable=True
    )
    
    verified_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    station_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("stations.id", ondelete="SET NULL"), nullable=True
    )
    
    # Timestamps for specific actions
    entry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    exit_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Additional Context
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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
    # Relationships
    # ---------------------------------------------------------
    
    # Link back to Registration (1-to-1)
    registration: Mapped["Registration"] = relationship(
        "Registration", back_populates="attendance"
    )
    
    # Link back to the Admin/Checker who verified the record
    verifier: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[verified_by],
        back_populates="verified_attendances"
    )
    
    # Link to the station where verification happened
    station: Mapped[Optional["Station"]] = relationship(
        "Station", back_populates="attendances"
    )