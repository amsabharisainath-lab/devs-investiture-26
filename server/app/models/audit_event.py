from datetime import datetime
from typing import Optional, Any, Dict,TYPE_CHECKING
from sqlalchemy import BigInteger, String, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

if TYPE_CHECKING:
    from app.models.user import User

from app.db.session import Base
from app.enum.audit_event_type import AuditEventType

class AuditEvent(Base):
    __tablename__ = "audit_events"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Actor Details (Nullable for system-generated events)
    actor_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    # Event Classification
    event_type: Mapped[AuditEventType] = mapped_column(Enum(AuditEventType), nullable=False)
    
    # Polymorphic Target Association (Generic Foreign Key)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    
    # Structured Metadata (Using PostgreSQL JSONB for indexing and query support)
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Server-Side Audit Timestamp (Notice: No updated_at for append-only tables)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------
    
    # Link back to the User who performed the action (if not system-generated)
    # actor: Mapped[Optional["User"]] = relationship(
    #     "User",
    #     foreign_keys=[actor_id],
    #     back_populates="audit_events"
    # )