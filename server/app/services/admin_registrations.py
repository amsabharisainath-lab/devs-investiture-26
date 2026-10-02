from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased

from app.enum.attendance_status import AttendanceDecision, AttendanceStatus
from app.enum.registration_status import RegistrationStatus
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.registration import Registration
from app.models.scan_event import ScanEvent
from app.models.station import Station
from app.models.user import User
from app.schemas.admin_registration import (
    AdminAttendanceDetail,
    AdminPagination,
    AdminRegistrationDetailResponse,
    AdminRegistrationItem,
    AdminRegistrationListResponse,
    AdminScanHistoryItem,
    AdminStudentSummary,
)


def _student_summary(user: User) -> AdminStudentSummary:
    return AdminStudentSummary(
        id=user.id,
        name=user.name,
        email=user.email,
        roll_no=user.roll_no,
        department=user.department,
        year=user.year,
    )


def _registration_item(
    registration: Registration,
    user: User,
    attendance: Attendance | None,
) -> AdminRegistrationItem:
    return AdminRegistrationItem(
        registration_id=registration.id,
        student=_student_summary(user),
        registration_status=registration.status,
        registration_source=registration.registration_source,
        registered_at=registration.registered_at,
        entry_status=attendance.entry_status if attendance else None,
        exit_status=attendance.exit_status if attendance else None,
        decision=attendance.decision if attendance else None,
        entry_at=attendance.entry_at if attendance else None,
        exit_at=attendance.exit_at if attendance else None,
    )


def _contains_pattern(value: str) -> str:
    escaped = (
        value.strip()
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
    return f"%{escaped}%"


def list_admin_registrations(
    db: Session,
    event_id: int,
    *,
    search: str | None,
    name: str | None,
    roll_no: str | None,
    year: int | None,
    department: str | None,
    registration_status: RegistrationStatus | None,
    entry_status: AttendanceStatus | None,
    exit_status: AttendanceStatus | None,
    decision: AttendanceDecision | None,
    unverified_only: bool,
    forgery_only: bool,
    sort_by: str,
    sort_order: str,
    page: int,
    page_size: int,
) -> AdminRegistrationListResponse | None:
    if db.get(Event, event_id) is None:
        return None

    query = (
        select(Registration, User, Attendance)
        .select_from(Registration)
        .join(User, User.id == Registration.user_id)
        .outerjoin(
            Attendance,
            Attendance.registration_id == Registration.id,
        )
        .where(Registration.event_id == event_id)
    )

    if search and search.strip():
        pattern = _contains_pattern(search)
        query = query.where(
            or_(
                User.name.ilike(pattern, escape="\\"),
                User.roll_no.ilike(pattern, escape="\\"),
                User.email.ilike(pattern, escape="\\"),
            )
        )
    if name and name.strip():
        query = query.where(
            User.name.ilike(_contains_pattern(name), escape="\\")
        )
    if roll_no and roll_no.strip():
        query = query.where(
            User.roll_no.ilike(_contains_pattern(roll_no), escape="\\")
        )
    if year is not None:
        query = query.where(User.year == year)
    if department and department.strip():
        query = query.where(
            func.lower(User.department) == department.strip().lower()
        )
    if registration_status is not None:
        query = query.where(Registration.status == registration_status)
    if entry_status is not None:
        query = query.where(Attendance.entry_status == entry_status)
    if exit_status is not None:
        query = query.where(Attendance.exit_status == exit_status)
    if decision is not None:
        query = query.where(Attendance.decision == decision)
    if unverified_only:
        query = query.where(Attendance.decision.is_(None))
    if forgery_only:
        query = query.where(
            Attendance.decision == AttendanceDecision.FORGERY
        )

    total = db.scalar(
        select(func.count()).select_from(query.subquery())
    ) or 0

    sort_columns = {
        "registered_at": Registration.registered_at,
        "name": func.lower(User.name),
        "roll_no": func.lower(User.roll_no),
    }
    sort_column = sort_columns[sort_by]
    ordering = (
        sort_column.desc().nullslast()
        if sort_order == "desc"
        else sort_column.asc().nullslast()
    )

    rows = db.execute(
        query.order_by(ordering, Registration.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return AdminRegistrationListResponse(
        items=[
            _registration_item(registration, user, attendance)
            for registration, user, attendance in rows
        ],
        pagination=AdminPagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size,
        ),
    )


def get_admin_registration_detail(
    db: Session,
    event_id: int,
    registration_id: int,
) -> AdminRegistrationDetailResponse | None:
    row = db.execute(
        select(Registration, User, Attendance)
        .select_from(Registration)
        .join(User, User.id == Registration.user_id)
        .outerjoin(
            Attendance,
            Attendance.registration_id == Registration.id,
        )
        .where(
            Registration.event_id == event_id,
            Registration.id == registration_id,
        )
    ).one_or_none()

    if row is None:
        return None

    registration, user, attendance = row

    attendance_detail = None
    if attendance is not None:
        attendance_station = (
            db.get(Station, attendance.station_id)
            if attendance.station_id is not None
            else None
        )
        attendance_detail = AdminAttendanceDetail(
            id=attendance.id,
            entry_status=attendance.entry_status,
            exit_status=attendance.exit_status,
            decision=attendance.decision,
            verified_by=attendance.verified_by,
            station_id=attendance.station_id,
            station_name=(
                attendance_station.name if attendance_station else None
            ),
            entry_at=attendance.entry_at,
            exit_at=attendance.exit_at,
            verified_at=attendance.verified_at,
            reason=attendance.reason,
        )

    actor = aliased(User)
    scan_history_query = (
        select(
            ScanEvent,
            actor.name.label("actor_name"),
            Station.name.label("station_name"),
        )
        .select_from(ScanEvent)
        .outerjoin(actor, ScanEvent.actor_id == actor.id)
        .outerjoin(Station, ScanEvent.station_id == Station.id)
        .where(ScanEvent.registration_id == registration_id)
    )

    scan_history_total = db.scalar(
        select(func.count(ScanEvent.id)).where(
            ScanEvent.registration_id == registration_id
        )
    ) or 0

    scan_history_rows = db.execute(
        scan_history_query
        .order_by(ScanEvent.receipt_at.desc(), ScanEvent.id.desc())
        .limit(50)
    ).all()

    return AdminRegistrationDetailResponse(
        registration=_registration_item(registration, user, attendance),
        attendance=attendance_detail,
        scan_history=[
            AdminScanHistoryItem(
                id=scan_event.id,
                token_id=scan_event.token_id,
                action=scan_event.action,
                result=scan_event.result,
                reason=scan_event.reason,
                actor_id=scan_event.actor_id,
                actor_name=actor_name,
                station_id=scan_event.station_id,
                station_name=station_name,
                receipt_at=scan_event.receipt_at,
            )
            for scan_event, actor_name, station_name in scan_history_rows
        ],
        scan_history_total=scan_history_total,
    )
