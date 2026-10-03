from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased

from app.enum.qr_action import QRAction
from app.enum.scan_result import ScanResult
from app.models.event import Event
from app.models.registration import Registration
from app.models.scan_event import ScanEvent
from app.models.station import Station
from app.models.user import User
from app.schemas.admin_scan_history import (
    AdminScanHistoryItem,
    AdminScanHistoryResponse,
    ScanHistoryActor,
    ScanHistoryEventSummary,
    ScanHistoryPagination,
    ScanHistoryStationSummary,
    ScannedStudentSummary,
)


class ScanActorNotFoundError(LookupError):
    pass


def _contains_pattern(value: str) -> str:
    escaped = (
        value.strip()
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
    return f"%{escaped}%"


def list_scans_by_actor(
    db: Session,
    *,
    actor_id: int,
    search: str | None,
    event_id: int | None,
    station_id: int | None,
    action: QRAction | None,
    result: ScanResult | None,
    date_from: datetime | None,
    date_to: datetime | None,
    page: int,
    page_size: int,
) -> AdminScanHistoryResponse:
    actor = db.get(User, actor_id)
    if actor is None:
        raise ScanActorNotFoundError("User not found")

    student = aliased(User)

    query = (
        select(ScanEvent, Registration, student, Event, Station)
        .select_from(ScanEvent)
        .outerjoin(
            Registration,
            Registration.id == ScanEvent.registration_id,
        )
        .outerjoin(student, student.id == Registration.user_id)
        .outerjoin(Event, Event.id == Registration.event_id)
        .outerjoin(Station, Station.id == ScanEvent.station_id)
        .where(ScanEvent.actor_id == actor_id)
    )

    if search and search.strip():
        pattern = _contains_pattern(search)
        query = query.where(
            or_(
                student.name.ilike(pattern, escape="\\"),
                student.roll_no.ilike(pattern, escape="\\"),
                student.email.ilike(pattern, escape="\\"),
            )
        )
    if event_id is not None:
        query = query.where(Registration.event_id == event_id)
    if station_id is not None:
        query = query.where(ScanEvent.station_id == station_id)
    if action is not None:
        query = query.where(ScanEvent.action == action)
    if result is not None:
        query = query.where(ScanEvent.result == result)
    if date_from is not None:
        query = query.where(ScanEvent.receipt_at >= date_from)
    if date_to is not None:
        query = query.where(ScanEvent.receipt_at <= date_to)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0

    rows = db.execute(
        query.order_by(
            ScanEvent.receipt_at.desc(),
            ScanEvent.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    items = []
    for scan, registration, scanned_student, event, station in rows:
        items.append(
            AdminScanHistoryItem(
                scan_id=scan.id,
                token_id=scan.token_id,
                registration_id=(registration.id if registration is not None else None),
                student=(
                    ScannedStudentSummary(
                        id=scanned_student.id,
                        name=scanned_student.name,
                        email=scanned_student.email,
                        roll_no=scanned_student.roll_no,
                        department=scanned_student.department,
                        year=scanned_student.year,
                    )
                    if scanned_student is not None
                    else None
                ),
                event=(
                    ScanHistoryEventSummary(id=event.id, name=event.name)
                    if event is not None
                    else None
                ),
                station=(
                    ScanHistoryStationSummary(
                        id=station.id,
                        name=station.name,
                        type=station.type,
                    )
                    if station is not None
                    else None
                ),
                action=scan.action,
                result=scan.result,
                reason=scan.reason,
                receipt_at=scan.receipt_at,
            )
        )

    return AdminScanHistoryResponse(
        actor=ScanHistoryActor(
            id=actor.id,
            name=actor.name,
            email=actor.email,
            role=actor.role,
        ),
        items=items,
        pagination=ScanHistoryPagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size,
        ),
    )
