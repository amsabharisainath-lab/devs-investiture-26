import logging
from typing import Literal

from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.enum.user_role import UserRole
from app.models.station import Station
from app.models.user import User


logger = logging.getLogger(__name__)


class UserNotFoundError(LookupError):
    pass


class RoleChangeConflictError(ValueError):
    pass


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _contains(column, value: str):
    return column.ilike(f"%{_escape_like(value)}%", escape="\\")


def _user_data(user: User) -> dict:
    stations = sorted(user.assigned_stations, key=lambda item: (item.name.lower(), item.id))
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "roll_no": user.roll_no,
        "department": user.department,
        "year": user.year,
        "role": user.role,
        "is_active": user.is_active,
        "assigned_stations": [
            {
                "id": station.id,
                "name": station.name,
                "type": station.type,
                "active": station.active,
            }
            for station in stations
        ],
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


def _load_user(db: Session, user_id: int) -> User | None:
    return (
        db.query(User)
        .options(selectinload(User.assigned_stations))
        .filter(User.id == user_id)
        .one_or_none()
    )


def list_users(
    db: Session,
    *,
    search: str | None,
    role: UserRole | None,
    is_active: bool | None,
    sort_by: Literal["created_at", "name", "email"],
    sort_order: Literal["asc", "desc"],
    page: int,
    page_size: int,
) -> dict:
    filters = []

    if search and (term := search.strip()):
        filters.append(
            or_(
                _contains(User.name, term),
                _contains(User.email, term),
                _contains(User.roll_no, term),
            )
        )
    if role is not None:
        filters.append(User.role == role)
    if is_active is not None:
        filters.append(User.is_active.is_(is_active))

    total = db.query(func.count(User.id)).filter(*filters).scalar() or 0

    sort_column = {
        "created_at": User.created_at,
        "name": User.name,
        "email": User.email,
    }[sort_by]
    order_expression = sort_column.asc() if sort_order == "asc" else sort_column.desc()
    tie_breaker = User.id.asc() if sort_order == "asc" else User.id.desc()

    users = (
        db.query(User)
        .options(selectinload(User.assigned_stations))
        .filter(*filters)
        .order_by(order_expression, tie_breaker)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [_user_data(user) for user in users],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


def change_user_role(
    db: Session,
    *,
    user_id: int,
    new_role: UserRole,
    changed_by_user_id: int,
) -> dict:
    # Lock active super admins in a stable order. This prevents two concurrent
    # requests from both removing the final usable SUPER_ADMIN.
    active_super_admins = (
        db.query(User)
        .filter(
            User.role == UserRole.SUPER_ADMIN,
            User.is_active.is_(True),
        )
        .order_by(User.id.asc())
        .with_for_update()
        .all()
    )

    target = next((user for user in active_super_admins if user.id == user_id), None)
    if target is None:
        target = (
            db.query(User)
            .filter(User.id == user_id)
            .with_for_update()
            .one_or_none()
        )

    if target is None:
        db.rollback()
        raise UserNotFoundError("User not found")

    old_role = target.role
    if old_role == new_role:
        db.rollback()
        current = _load_user(db, user_id)
        return _user_data(current)

    if target.id == changed_by_user_id and new_role != UserRole.SUPER_ADMIN:
        db.rollback()
        raise RoleChangeConflictError("You cannot remove your own SUPER_ADMIN role")

    if (
        target.is_active
        and old_role == UserRole.SUPER_ADMIN
        and new_role != UserRole.SUPER_ADMIN
        and len(active_super_admins) <= 1
    ):
        db.rollback()
        raise RoleChangeConflictError("The final active SUPER_ADMIN cannot be demoted")

    target.role = new_role

    # Students must never retain scanner-station assignments.
    if new_role == UserRole.STUDENT:
        assigned_stations = (
            db.query(Station)
            .filter(Station.assigned_admin_id == target.id)
            .order_by(Station.id.asc())
            .with_for_update()
            .all()
        )
        for station in assigned_stations:
            station.assigned_admin_id = None

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    logger.info(
        "user role changed actor_id=%s target_user_id=%s old_role=%s new_role=%s",
        changed_by_user_id,
        user_id,
        old_role.value,
        new_role.value,
    )

    updated = _load_user(db, user_id)
    return _user_data(updated)
