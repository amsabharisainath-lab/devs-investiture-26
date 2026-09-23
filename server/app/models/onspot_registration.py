from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class OnSpotRegistration(Base):
    """
    Tracks the email an admin was told to expect for an on-spot
    registration, so a later Google login can be matched back to the
    User/Registration created at the venue instead of creating a
    duplicate User.
    """
    __tablename__ = "onspot_registrations"
    __table_args__ = (
        # One on-spot record per registration — this is a 1:1 link,
        # not a log of multiple attempts.
        UniqueConstraint("registration_id", name="uq_onspot_registration_id"),
        Index("ix_onspot_submitted_email", "submitted_email"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    registration_id: Mapped[int] = mapped_column(
        ForeignKey("registrations.id"), nullable=False
    )
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)

    # Always store normalized (lowercased, trimmed) — this is the
    # matching key against Google's verified email later.
    submitted_email: Mapped[str] = mapped_column(String(320), nullable=False)

    # Who at the venue took the registration — for audit purposes.
    registered_by_admin_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Set the moment a Google login successfully attaches google_sub
    # to the linked User. NULL means "still waiting to be claimed."
    claimed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="onspot_registration"
    )
    registered_by: Mapped["User"] = relationship(
        "User", foreign_keys=[registered_by_admin_id]
    )
    registration: Mapped["Registration"] = relationship(
        "Registration", back_populates="onspot_record"
    )
    event: Mapped["Event"] = relationship("Event")