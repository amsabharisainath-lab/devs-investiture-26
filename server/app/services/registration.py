from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependancies.create_qr import create_qr
from app.enum.attendance_status import AttendanceStatus
from app.enum.registration_source import RegistrationSource
from app.enum.registration_status import RegistrationStatus
from app.enum.user_role import UserRole
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.registration import Registration
from app.models.user import User
from app.models.qr_token import QRToken
from app.enum.qr_action import QRAction
from datetime import datetime


class RegistrationError(Exception):
    pass


class EventNotFoundError(RegistrationError):
    pass


class ProfileIncompleteError(RegistrationError):
    pass


class AlreadyRegisteredError(RegistrationError):
    pass


class StudentRoleRequiredError(RegistrationError):
    pass


class QRIssuanceFailedError(RegistrationError):
    def __init__(self, detail: str, status_code: int):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


def profile_is_complete(user: User) -> bool:
    required_values = (
        user.name,
        user.roll_no,
        user.department,
        user.year,
    )
    return all(
        value is not None and (not isinstance(value, str) or value.strip())
        for value in required_values
    )


def register_for_event(
    *,
    event_id: int,
    user: User,
    db: Session,
) -> tuple[Registration, str, "datetime | None"]:
    if user.role != UserRole.STUDENT:
        raise StudentRoleRequiredError

    if not profile_is_complete(user):
        raise ProfileIncompleteError

    event = db.get(Event, event_id)
    if event is None:
        raise EventNotFoundError

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
        registration_source=RegistrationSource.SELF,
    )
    db.add(registration)

    try:
        db.flush()  # registration.id exists, not yet committed

        attendance = Attendance(
            registration_id=registration.id,
            entry_status=AttendanceStatus.PENDING,
            exit_status=AttendanceStatus.PENDING,
        )
        db.add(attendance)

        # Registration + attendance commit together.
        # create_qr is intentionally NOT called before this commit —
        # it expects registration.attendance to already be persisted.
        db.commit()

    except IntegrityError as exc:
        db.rollback()
        raise AlreadyRegisteredError from exc

    db.refresh(registration)

    # Second step: create_qr commits internally and owns its own
    # success/error shape. We translate its (dict, status_code)
    # return into an exception so the router can handle it uniformly.
    result, status_code = create_qr(
        registration_id=registration.id,
        action_str="ENTRY",
        db_session=db,
    )

    if status_code != 200:
        raise QRIssuanceFailedError(
            detail=result.get("error", "QR issuance failed."),
            status_code=status_code,
        )

    raw_token = result["token"]

    # create_qr's success payload doesn't include expires_at, so we
    # re-fetch the row it just wrote. Safe because create_qr already
    # committed, and this is a read-only query on our own session.
    qr_token = (
        db.query(QRToken)
        .filter(
            QRToken.registration_id == registration.id,
            QRToken.action == QRAction.ENTRY,
        )
        .first()
    )
    expires_at = qr_token.expires_at if qr_token else None

    return registration, raw_token, expires_at