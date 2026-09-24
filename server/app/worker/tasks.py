import logging

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.registration import Registration
from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    ignore_result=True,
)
def send_registration_email(self, registration_id: int) -> None:
    """Load a registration and invoke the existing email sender.

    The sender is imported lazily so the API process does not need to
    initialize email infrastructure just to enqueue a task.
    """
    db: Session = SessionLocal()
    try:
        registration = db.get(Registration, registration_id)
        if registration is None:
            raise ValueError(f"Registration {registration_id} was not found")

        from app.services.registration_email import send_registration_email_now

        send_registration_email_now(registration, db)
    finally:
        db.close()


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    ignore_result=True,
)
def send_od_email(self, od_id: int) -> None:
    """Temporary OD queue placeholder until the real OD sender is ready."""
    logger.info("[DUMMY OD TASK] Processing OD %s", od_id)
