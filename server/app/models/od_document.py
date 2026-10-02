from datetime import datetime
from sqlalchemy import BigInteger, String, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.registration import Registration

from app.db.session import Base
from app.enum.od_status import ODStatus

class ODDocument(Base):
    __tablename__ = "od_documents"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign Keys
    registration_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("registrations.id", ondelete="RESTRICT"), 
        nullable=False, 
        index=True
    )
    
    # Document Metadata
    file_path: Mapped[str] = mapped_column(String(512), nullable=True)
    
    # Storing standard SHA-256 hex digest requires exactly 64 characters
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    
    status: Mapped[ODStatus] = mapped_column(
        Enum(ODStatus), nullable=False, default=ODStatus.GENERATED
    )

    # Timestamps
    generated_at: Mapped[datetime] = mapped_column(
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
    
    # Link back to the Registration
    registration: Mapped["Registration"] = relationship(
        "Registration", back_populates="od_documents"
    )