from datetime import datetime
from typing import List, Optional,TYPE_CHECKING
from sqlalchemy import BigInteger,Integer, String, Boolean, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.scan_event import ScanEvent
    from app.models.attendance import Attendance

# Assuming your declarative base is imported from core
from app.db.session import Base
from app.enum.station_type import StationType

class Station(Base):
    __tablename__ = "stations"
    ID_TYPE = BigInteger().with_variant(Integer, "sqlite")

    # Primary Key
    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)

    # Station Details
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    type: Mapped[StationType] = mapped_column(Enum(StationType), nullable=False)
    
    # Availability
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)

    # Foreign Keys
    assigned_admin_id: Mapped[Optional[int]] = mapped_column(
        ID_TYPE, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Timestamps
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
    
    # Link back to the User (Checker/Admin) assigned to this station
    assigned_admin: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[assigned_admin_id],
        back_populates="assigned_stations"
    )
    
    # Historical scans performed at this station
    scan_events: Mapped[List["ScanEvent"]] = relationship(
        "ScanEvent", back_populates="station"
    )
    
    # Attendances verified/processed at this station
    attendances: Mapped[List["Attendance"]] = relationship(
        "Attendance", back_populates="station"
    )