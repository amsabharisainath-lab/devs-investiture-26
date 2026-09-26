import logging
import hashlib
import smtplib

from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models.registration import Registration
from app.worker.celery_app import celery_app

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.worker.celery_app import celery_app

# Import your models and enums
from app.models.event import Event
from app.models.registration import Registration
from app.models.user import User, UserRole  
from app.models.attendance import Attendance, AttendanceDecision
from app.models.od_document import ODDocument, ODStatus

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



# ---------------------------------------------------------------------------
# 1. BULK TASK (Coordinator)
# ---------------------------------------------------------------------------
@celery_app.task(ignore_result=True)
def send_bulk_od(event_id: int) -> None:
    """Coordinator task: Validates event, finds eligible students, enqueues single tasks."""
    db: Session = SessionLocal()
    try:
        event = db.get(Event, event_id)
        if not event:
            logger.error("[BULK OD] Event %s does not exist. Aborting.", event_id)
            return

        # Adjust 'end_time' to your exact Event model field
        if event.end_time > datetime.now(timezone.utc):
            logger.warning("[BULK OD] Event %s has not ended yet. Aborting.", event_id)
            return

        # Find eligible registrations strictly using Enums
        eligible_registrations = (
            db.query(Registration)
            .join(Registration.user)
            .join(Registration.attendance)
            .filter(
                Registration.event_id == event_id,
                User.role == UserRole.STUDENT,
                Attendance.decision == AttendanceDecision.PRESENT,
            )
            .all()
        )

        logger.info(
            "[BULK OD] Found %d eligible students for event %s",
            len(eligible_registrations),
            event_id,
        )

        # Enqueue individual tasks (Fire and forget)
        for reg in eligible_registrations:
            send_single_od.delay(reg.id)

    except Exception:
        logger.exception("[BULK OD] Unexpected error processing event %s", event_id)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 2. SINGLE TASK (Worker)
# ---------------------------------------------------------------------------
@celery_app.task(
    autoretry_for=(smtplib.SMTPException,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    ignore_result=True,
)
def send_single_od(registration_id: int) -> None:
    """Handles ONE student: Idempotency check, PDF gen, DB update, Email send."""
    db: Session = SessionLocal()
    try:
        # 1. Fetch registration with related user and attendance
        registration = (
            db.query(Registration)
            .join(Registration.user)
            .join(Registration.attendance)
            .filter(Registration.id == registration_id)
            .first()
        )

        if not registration:
            logger.error("[SINGLE OD] Registration %s not found.", registration_id)
            return

        # 2. Re-verify STUDENT and PRESENT status (in case state changed)
        if (
            registration.user.role != UserRole.STUDENT
            or registration.attendance.decision != AttendanceDecision.PRESENT
        ):
            logger.warning("[SINGLE OD] Registration %s is not eligible. Skipping.", registration_id)
            return

        # 3. Check Idempotency (Already SENT?)
        od_doc = db.query(ODDocument).filter(ODDocument.registration_id == registration_id).first()
        if od_doc and od_doc.status == ODStatus.SENT:
            logger.info("[SINGLE OD] OD for Registration %s already SENT. Skipping.", registration_id)
            return

        # 4. Extract required student information
        user = registration.user
        student_email = user.email

        # 5. Generate PDF
        from app.dependancies.create_od_pdf import create_od_pdf
        
        pdf_bytes = create_od_pdf(
            department_name=user.department_name,
            student_name=user.name,
            roll_number=user.roll_number,
            year=user.year
        )

        # 6. Calculate SHA-256
        sha256_hash = hashlib.sha256(pdf_bytes).hexdigest()

        # 7. Create or update ODDocument as GENERATED
        if not od_doc:
            od_doc = ODDocument(
                registration_id=registration_id,
                file_path=None,
                sha256=sha256_hash,
                status=ODStatus.GENERATED,
            )
            db.add(od_doc)
        else:
            od_doc.sha256 = sha256_hash
            od_doc.status = ODStatus.GENERATED
            od_doc.file_path = None
            
        db.commit()

        # 8. Send Email
        from app.dependancies.send_email import send_email;

        try:
            send_email(
                receiver_email=student_email,
                subject=f"OD Document - {user.name}",
                html_content="<p>Please find your Official Duty (OD) document attached.</p>",
                pdf_bytes=pdf_bytes,
                pdf_filename=f"OD_{user.roll_number}.pdf"
            )
        except Exception:
            logger.exception("[SINGLE OD] Email failed for registration %s", registration_id)
            raise

        # 9. Email succeeded: mark as SENT
        od_doc.status = ODStatus.SENT
        db.commit()
        logger.info("[SINGLE OD] Successfully sent OD to registration %s", registration_id)

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
