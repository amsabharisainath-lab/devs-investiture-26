from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependancies.create_qr import create_qr
from app.enum.attendance_status import AttendanceStatus
from app.enum.qr_action import QRAction
from app.enum.registration_source import RegistrationSource
from app.enum.registration_status import RegistrationStatus
from app.enum.user_role import UserRole
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.onspot_registration import OnSpotRegistration
from app.models.registration import Registration
from app.models.user import User


class OnSpotRegistrationError(Exception):
    pass


class EventNotFoundError(OnSpotRegistrationError):
    pass


class AlreadyRegisteredError(OnSpotRegistrationError):
    pass


class QRIssuanceFailedError(OnSpotRegistrationError):
    def __init__(self, result: dict, status_code: int):
        self.result = result
        self.status_code = status_code
        super().__init__(result.get("error", "QR issuance failed."))


def get_or_create_onspot_user(
    *,
    email: str,
    name: str,
    roll_no: str,
    department: str,
    year: int,
    db: Session,
) -> User:
    """
    Looks up a User by normalized email first. Reuses the row if it
    already exists (e.g. already logged in via Google before, or was
    on-spot-registered at a prior event). Only creates a new User
    with google_sub=NULL when no match exists at all.
    """
    normalized_email = email.strip().lower()

    existing_user = (
        db.query(User).filter(User.email == normalized_email).one_or_none()
    )
    if existing_user:
        return existing_user

    user = User(
        email=normalized_email,
        name=name,
        roll_no=roll_no,
        department=department,
        year=year,
        role=UserRole.STUDENT,
        google_sub=None,
    )
    db.add(user)
    db.flush()  # get user.id without committing yet
    return user


def register_onspot(
    *,
    event_id: int,
    email: str,
    name: str,
    roll_no: str,
    department: str,
    year: int,
    admin: User,
    db: Session,
) -> tuple[Registration, OnSpotRegistration, str, str | None]:
    event = db.get(Event, event_id)
    if event is None:
        raise EventNotFoundError

    user = get_or_create_onspot_user(
        email=email,
        name=name,
        roll_no=roll_no,
        department=department,
        year=year,
        db=db,
    )

    existing_registration = (
        db.query(Registration)
        .filter(
            Registration.event_id == event_id,
            Registration.user_id == user.id,
        )
        .one_or_none()
    )
    if existing_registration:
        raise AlreadyRegisteredError

    registration = Registration(
        event_id=event_id,
        user_id=user.id,
        status=RegistrationStatus.CONFIRMED,
        registration_source=RegistrationSource.ON_SPOT,
    )
    db.add(registration)

    try:
        db.flush()

        attendance = Attendance(
            registration_id=registration.id,
            entry_status=AttendanceStatus.PENDING,
            exit_status=AttendanceStatus.PENDING,
        )
        db.add(attendance)

        onspot_record = OnSpotRegistration(
            user_id=user.id,
            registration_id=registration.id,
            event_id=event_id,
            submitted_email=email.strip().lower(),
            registered_by_admin_id=admin.id,
        )
        db.add(onspot_record)

        # Registration + attendance + onspot record commit together.
        db.commit()

    except IntegrityError as exc:
        db.rollback()
        raise AlreadyRegisteredError from exc

    db.refresh(registration)
    db.refresh(onspot_record)

    result, status_code = create_qr(
        registration_id=registration.id,
        action_str="ENTRY",
        db_session=db,
    )

    if status_code != 200:
        raise QRIssuanceFailedError(result=result, status_code=status_code)

    return registration, onspot_record, result["token"], result.get("expires_at")