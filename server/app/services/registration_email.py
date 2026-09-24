from sqlalchemy.orm import Session

from app.dependancies.email_format import send_registration_email
from app.models.registration import Registration


def send_registration_email_now(
    registration: Registration,
    db: Session,
) -> None:
    """Send the existing formatted registration email for a persisted record."""
    if not registration.user or not registration.user.email:
        raise ValueError(
            f"Registration {registration.id} has no recipient email address"
        )

    if not send_registration_email(registration.user.email):
        raise RuntimeError(
            f"Registration email delivery failed for {registration.user.email}"
        )
