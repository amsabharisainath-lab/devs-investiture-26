from sqlalchemy.orm import Session

from app.models.registration import Registration


def send_registration_email_now(
    registration: Registration,
    db: Session,
) -> None:
    """Adapter for the project's existing registration email implementation.

    Keep the existing formatting and SMTP code in this function when it is
    available. The queue task owns only scheduling and database reloading.
    """
    raise NotImplementedError(
        "Connect send_registration_email_now to the existing registration "
        "email sender before enabling the worker."
    )
