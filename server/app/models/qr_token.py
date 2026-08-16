from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, ForeignKey, Enum, DateTime, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Assuming your declarative base is imported from core
from app.core.database import Base
from app.enums.qr_action import QRAction

class QRToken(Base):
    __tablename__ = "qr_tokens"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign Keys
    registration_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("registrations.id", ondelete="RESTRICT"), 
        nullable=False, 
        index=True
    )
    
    # Token Properties
    action: Mapped[QRAction] = mapped_column(Enum(QRAction), nullable=False)
    
    # Store only the hash, never the raw token string
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
    # Timestamps & Lifecycle
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ---------------------------------------------------------
    # Table Constraints
    # ---------------------------------------------------------
    __table_args__ = (
        CheckConstraint(
            "expires_at > issued_at", 
            name="check_expires_after_issued"
        ),
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------
    
    # Link back to the Registration
    registration: Mapped["Registration"] = relationship(
        "Registration", back_populates="qr_tokens"
    )

    scan_events: Mapped[List["ScanEvent"]] = relationship(
        "ScanEvent",
        back_populates="token"
    )