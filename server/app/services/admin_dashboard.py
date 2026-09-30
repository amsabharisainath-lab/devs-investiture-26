from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.enum.attendance_status import AttendanceDecision, AttendanceStatus
from app.enum.registration_status import RegistrationStatus
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.registration import Registration
from app.schemas.admin_dashboard import (
    AdminDashboardCounts,
    AdminDashboardResponse,
    AdminEventSummary,
)


def get_admin_dashboard(
    db: Session,
    event_id: int,
) -> AdminDashboardResponse | None:
    event = db.get(Event, event_id)
    if event is None:
        return None

    (
        registered,
        present,
        forgery,
        entered,
        exited,
        currently_inside,
    ) = db.execute(
        select(
            func.count(Registration.id),
            func.count(Registration.id).filter(
                Attendance.decision == AttendanceDecision.PRESENT
            ),
            func.count(Registration.id).filter(
                Attendance.decision == AttendanceDecision.FORGERY
            ),
            func.count(Registration.id).filter(
                Attendance.entry_status == AttendanceStatus.SCANNED
            ),
            func.count(Registration.id).filter(
                Attendance.exit_status == AttendanceStatus.SCANNED
            ),
            func.count(Registration.id).filter(
                and_(
                    Attendance.entry_status == AttendanceStatus.SCANNED,
                    Attendance.exit_status != AttendanceStatus.SCANNED,
                )
            ),
        )
        .select_from(Registration)
        .outerjoin(
            Attendance,
            Attendance.registration_id == Registration.id,
        )
        .where(
            Registration.event_id == event_id,
            Registration.status == RegistrationStatus.CONFIRMED,
        )
    ).one()

    return AdminDashboardResponse(
        event=AdminEventSummary(
            id=event.id,
            name=event.name,
            status=event.status,
            entry_open_at=event.entry_open_at,
            entry_close_at=event.entry_close_at,
            exit_open_at=event.exit_open_at,
            exit_close_at=event.exit_close_at,
        ),
        counts=AdminDashboardCounts(
            registered=registered,
            present=present,
            absent_or_unverified=max(registered - present - forgery, 0),
            forgery=forgery,
            entered=entered,
            exited=exited,
            currently_inside=currently_inside,
        ),
    )
