from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, ForeignKey, Enum, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Assuming your declarative base is imported from core
from app.core.database import Base
from app.enums.scan_result import ScanResult
from app.enums.qr_action import QRAction

class ScanEvent(Base):
    __tablename__ = "scan_events"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign Keys - Context (Nullable for completely invalid/unknown QR codes)
    registration_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("registrations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    token_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("qr_tokens.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    # Foreign Keys - Operational (Not Null)
    actor_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    station_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("stations.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    
    # Scan Details
    action: Mapped[QRAction] = mapped_column(Enum(QRAction), nullable=False)
    result: Mapped[ScanResult] = mapped_column(Enum(ScanResult), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Server-Side Audit Timestamp (Notice: No updated_at for append-only tables)
    receipt_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------
    
    # Link to Registration (if matched)
    registration: Mapped[Optional["Registration"]] = relationship(
        "Registration",
        back_populates="scan_events"
    )
    
    # Link to QR Token (if matched)
    token: Mapped[Optional["QRToken"]] = relationship(
        "QRToken",
        back_populates="scan_events"
    )
    
    # Link to the User (Checker/Operator) who performed the scan
    actor: Mapped["User"] = relationship(
        "User",
        foreign_keys=[actor_id],
        back_populates="scan_events"
    )
    
    # Link to the physical Station where the scan occurred
    station: Mapped["Station"] = relationship(
        "Station",
        foreign_keys=[station_id],
        back_populates="scan_events"
    )