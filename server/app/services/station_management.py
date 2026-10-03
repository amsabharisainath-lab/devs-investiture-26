import logging
from typing import Literal

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.enum.station_type import StationType
from app.enum.user_role import UserRole
from app.models.station import Station
from app.models.user import User


logger = logging.getLogger(__name__)


class StationNotFoundError(LookupError):
    pass


class AssigneeNotFoundError(LookupError):
    pass


class StationNameConflictError(ValueError):
    pass


class InvalidStationAssigneeError(ValueError):
    pass


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _contains(column, value: str):
    return column.ilike(f"%{_escape_like(value)}%", escape="\\")


def _station_data(station: Station) -> dict:
    admin = station.assigned_admin
    return {
        "id": station.id,
        "name": station.name,
        "type": station.type,
        "active": station.active,
        "assigned_admin": (
            {
                "id": admin.id,
                "name": admin.name,
                "email": admin.email,
                "role": admin.role,
                "is_active": admin.is_active,
            }
            if admin is not None
            else None
        ),
        "created_at": station.created_at,
        "updated_at": station.updated_at,
    }


def _load_station(db: Session, station_id: int) -> Station | None:
    return (
        db.query(Station)
        .options(joinedload(Station.assigned_admin))
        .filter(Station.id == station_id)
        .one_or_none()
    )


def list_stations(
    db: Session,
    *,
    search: str | None,
    station_type: StationType | None,
    active: bool | None,
    assigned: bool | None,
    assigned_admin_id: int | None,
    sort_by: Literal["created_at", "name"],
    sort_order: Literal["asc", "desc"],
    page: int,
    page_size: int,
) -> dict:
    filters = []

    if search and (term := search.strip()):
        filters.append(_contains(Station.name, term))
    if station_type is not None:
        filters.append(Station.type == station_type)
    if active is not None:
        filters.append(Station.active.is_(active))
    if assigned is True:
        filters.append(Station.assigned_admin_id.is_not(None))
    elif assigned is False:
        filters.append(Station.assigned_admin_id.is_(None))
    if assigned_admin_id is not None:
        filters.append(Station.assigned_admin_id == assigned_admin_id)

    total = db.query(func.count(Station.id)).filter(*filters).scalar() or 0

    sort_column = {
        "created_at": Station.created_at,
        "name": Station.name,
    }[sort_by]
    order_expression = sort_column.asc() if sort_order == "asc" else sort_column.desc()
    tie_breaker = Station.id.asc() if sort_order == "asc" else Station.id.desc()

    stations = (
        db.query(Station)
        .options(joinedload(Station.assigned_admin))
        .filter(*filters)
        .order_by(order_expression, tie_breaker)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [_station_data(station) for station in stations],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


def _ensure_unique_name(
    db: Session,
    name: str,
    *,
    excluding_station_id: int | None = None,
) -> None:
    query = db.query(Station.id).filter(func.lower(Station.name) == name.lower())
    if excluding_station_id is not None:
        query = query.filter(Station.id != excluding_station_id)
    if query.first() is not None:
        raise StationNameConflictError("A station with this name already exists")


def create_station(
    db: Session,
    *,
    name: str,
    station_type: StationType,
    active: bool,
    created_by_user_id: int,
) -> dict:
    try:
        _ensure_unique_name(db, name)
    except StationNameConflictError:
        db.rollback()
        raise

    station = Station(name=name, type=station_type, active=active)
    db.add(station)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise StationNameConflictError("A station with this name already exists") from exc
    except SQLAlchemyError:
        db.rollback()
        raise

    logger.info(
        "station created actor_id=%s station_id=%s",
        created_by_user_id,
        station.id,
    )
    created = _load_station(db, station.id)
    return _station_data(created)


def update_station(
    db: Session,
    *,
    station_id: int,
    name: str | None,
    station_type: StationType | None,
    active: bool | None,
    updated_by_user_id: int,
) -> dict:
    station = (
        db.query(Station)
        .filter(Station.id == station_id)
        .with_for_update()
        .one_or_none()
    )
    if station is None:
        db.rollback()
        raise StationNotFoundError("Station not found")

    if name is not None and name.lower() != station.name.lower():
        try:
            _ensure_unique_name(db, name, excluding_station_id=station.id)
        except StationNameConflictError:
            db.rollback()
            raise
        station.name = name
    elif name is not None:
        station.name = name

    if station_type is not None:
        station.type = station_type
    if active is not None:
        station.active = active

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise StationNameConflictError("A station with this name already exists") from exc
    except SQLAlchemyError:
        db.rollback()
        raise

    logger.info(
        "station updated actor_id=%s station_id=%s",
        updated_by_user_id,
        station_id,
    )
    updated = _load_station(db, station_id)
    return _station_data(updated)


def set_station_assignment(
    db: Session,
    *,
    station_id: int,
    assigned_admin_id: int | None,
    changed_by_user_id: int,
) -> dict:
    # Check first so a missing station is reported before a bad assignee id.
    station_exists = db.query(Station.id).filter(Station.id == station_id).scalar()
    if station_exists is None:
        db.rollback()
        raise StationNotFoundError("Station not found")

    assignee = None
    if assigned_admin_id is not None:
        # Lock the user before the station. Role changes use the same lock order.
        assignee = (
            db.query(User)
            .filter(User.id == assigned_admin_id)
            .with_for_update()
            .one_or_none()
        )
        if assignee is None:
            db.rollback()
            raise AssigneeNotFoundError("Assigned user not found")
        if not assignee.is_active:
            db.rollback()
            raise InvalidStationAssigneeError("An inactive user cannot be assigned")
        if assignee.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
            db.rollback()
            raise InvalidStationAssigneeError(
                "Only an ADMIN or SUPER_ADMIN can be assigned to a station"
            )

    station = (
        db.query(Station)
        .filter(Station.id == station_id)
        .with_for_update()
        .one_or_none()
    )
    if station is None:
        db.rollback()
        raise StationNotFoundError("Station not found")

    previous_admin_id = station.assigned_admin_id
    station.assigned_admin_id = assignee.id if assignee is not None else None

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    logger.info(
        "station assignment changed actor_id=%s station_id=%s old_admin_id=%s new_admin_id=%s",
        changed_by_user_id,
        station_id,
        previous_admin_id,
        assigned_admin_id,
    )
    updated = _load_station(db, station_id)
    return _station_data(updated)
