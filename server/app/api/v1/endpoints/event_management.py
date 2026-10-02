# import logging
# from datetime import datetime
# from typing import Literal

# from sqlalchemy import func, select
# from sqlalchemy.exc import IntegrityError, SQLAlchemyError
# from sqlalchemy.orm import Session

# from app.enum.event_status import EventStatus
# from app.models.event import Event
# from app.models.registration import Registration


# logger = logging.getLogger(__name__)


# class EventNotFoundError(LookupError):
#     pass


# class EventDeletionConflictError(ValueError):
#     pass


# class InvalidEventScheduleError(ValueError):
#     pass


# def _escape_like(value: str) -> str:
#     return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


# def _validate_schedule(
#     entry_open_at: datetime,
#     entry_close_at: datetime,
#     exit_open_at: datetime,
#     exit_close_at: datetime,
# ) -> None:
#     try:
#         schedule_is_valid = (
#             entry_open_at
#             < entry_close_at
#             <= exit_open_at
#             < exit_close_at
#         )
#     except TypeError as exc:
#         raise InvalidEventScheduleError(
#             "All event times must be timezone-aware and use compatible timezones"
#         ) from exc

#     if not schedule_is_valid:
#         raise InvalidEventScheduleError(
#             "Event times must satisfy: entry_open_at < entry_close_at "
#             "<= exit_open_at < exit_close_at"
#         )


# def _registration_count_expression():
#     return (
#         select(func.count(Registration.id))
#         .where(Registration.event_id == Event.id)
#         .correlate(Event)
#         .scalar_subquery()
#     )


# def _event_data(event: Event, registration_count: int) -> dict:
#     return {
#         "id": event.id,
#         "name": event.name,
#         "entry_open_at": event.entry_open_at,
#         "entry_close_at": event.entry_close_at,
#         "exit_open_at": event.exit_open_at,
#         "exit_close_at": event.exit_close_at,
#         "status": event.status,
#         "registration_count": registration_count,
#         "can_delete": registration_count == 0,
#         "created_at": event.created_at,
#         "updated_at": event.updated_at,
#     }


# def list_events(
#     db: Session,
#     *,
#     search: str | None,
#     event_status: EventStatus | None,
#     sort_by: Literal["created_at", "name", "entry_open_at"],
#     sort_order: Literal["asc", "desc"],
#     page: int,
#     page_size: int,
# ) -> dict:
#     filters = []
#     if search and (term := search.strip()):
#         pattern = f"%{_escape_like(term)}%"
#         filters.append(Event.name.ilike(pattern, escape="\\"))
#     if event_status is not None:
#         filters.append(Event.status == event_status)

#     total = db.scalar(
#         select(func.count(Event.id)).where(*filters)
#     ) or 0

#     sort_column = {
#         "created_at": Event.created_at,
#         "name": func.lower(Event.name),
#         "entry_open_at": Event.entry_open_at,
#     }[sort_by]
#     ordering = (
#         sort_column.asc()
#         if sort_order == "asc"
#         else sort_column.desc()
#     )
#     tie_breaker = Event.id.asc() if sort_order == "asc" else Event.id.desc()

#     registration_count = _registration_count_expression().label(
#         "registration_count"
#     )
#     rows = db.execute(
#         select(Event, registration_count)
#         .where(*filters)
#         .order_by(ordering, tie_breaker)
#         .offset((page - 1) * page_size)
#         .limit(page_size)
#     ).all()

#     return {
#         "items": [
#             _event_data(event, count)
#             for event, count in rows
#         ],
#         "pagination": {
#             "page": page,
#             "page_size": page_size,
#             "total": total,
#             "total_pages": (total + page_size - 1) // page_size,
#         },
#     }


# def get_event(db: Session, *, event_id: int) -> dict:
#     registration_count = _registration_count_expression().label(
#         "registration_count"
#     )
#     row = db.execute(
#         select(Event, registration_count).where(Event.id == event_id)
#     ).one_or_none()
#     if row is None:
#         raise EventNotFoundError("Event not found")

#     event, count = row
#     return _event_data(event, count)


# def create_event(
#     db: Session,
#     *,
#     name: str,
#     entry_open_at: datetime,
#     entry_close_at: datetime,
#     exit_open_at: datetime,
#     exit_close_at: datetime,
#     event_status: EventStatus,
#     created_by_user_id: int,
# ) -> dict:
#     _validate_schedule(
#         entry_open_at,
#         entry_close_at,
#         exit_open_at,
#         exit_close_at,
#     )

#     event = Event(
#         name=name,
#         entry_open_at=entry_open_at,
#         entry_close_at=entry_close_at,
#         exit_open_at=exit_open_at,
#         exit_close_at=exit_close_at,
#         status=event_status,
#     )
#     db.add(event)

#     try:
#         db.commit()
#     except SQLAlchemyError:
#         db.rollback()
#         raise

#     logger.info(
#         "event created actor_id=%s event_id=%s",
#         created_by_user_id,
#         event.id,
#     )
#     return get_event(db, event_id=event.id)


# def update_event(
#     db: Session,
#     *,
#     event_id: int,
#     name: str | None,
#     entry_open_at: datetime | None,
#     entry_close_at: datetime | None,
#     exit_open_at: datetime | None,
#     exit_close_at: datetime | None,
#     event_status: EventStatus | None,
#     updated_by_user_id: int,
# ) -> dict:
#     event = (
#         db.query(Event)
#         .filter(Event.id == event_id)
#         .with_for_update()
#         .one_or_none()
#     )
#     if event is None:
#         db.rollback()
#         raise EventNotFoundError("Event not found")

#     new_entry_open_at = (
#         entry_open_at if entry_open_at is not None else event.entry_open_at
#     )
#     new_entry_close_at = (
#         entry_close_at if entry_close_at is not None else event.entry_close_at
#     )
#     new_exit_open_at = (
#         exit_open_at if exit_open_at is not None else event.exit_open_at
#     )
#     new_exit_close_at = (
#         exit_close_at if exit_close_at is not None else event.exit_close_at
#     )
#     try:
#         _validate_schedule(
#             new_entry_open_at,
#             new_entry_close_at,
#             new_exit_open_at,
#             new_exit_close_at,
#         )
#     except InvalidEventScheduleError:
#         db.rollback()
#         raise

#     if name is not None:
#         event.name = name
#     event.entry_open_at = new_entry_open_at
#     event.entry_close_at = new_entry_close_at
#     event.exit_open_at = new_exit_open_at
#     event.exit_close_at = new_exit_close_at
#     if event_status is not None:
#         event.status = event_status

#     try:
#         db.commit()
#     except SQLAlchemyError:
#         db.rollback()
#         raise

#     logger.info(
#         "event updated actor_id=%s event_id=%s",
#         updated_by_user_id,
#         event_id,
#     )
#     return get_event(db, event_id=event_id)


# def delete_event(
#     db: Session,
#     *,
#     event_id: int,
#     deleted_by_user_id: int,
# ) -> None:
#     event = (
#         db.query(Event)
#         .filter(Event.id == event_id)
#         .with_for_update()
#         .one_or_none()
#     )
#     if event is None:
#         db.rollback()
#         raise EventNotFoundError("Event not found")

#     registration_count = db.scalar(
#         select(func.count(Registration.id)).where(
#             Registration.event_id == event_id
#         )
#     ) or 0
#     if registration_count > 0:
#         db.rollback()
#         raise EventDeletionConflictError(
#             "An event with registrations cannot be deleted; "
#             "set its status to CANCELLED instead"
#         )

#     db.delete(event)
#     try:
#         db.commit()
#     except IntegrityError as exc:
#         db.rollback()
#         raise EventDeletionConflictError(
#             "The event is already referenced and cannot be deleted; "
#             "set its status to CANCELLED instead"
#         ) from exc
#     except SQLAlchemyError:
#         db.rollback()
#         raise

#     logger.info(
#         "event deleted actor_id=%s event_id=%s",
#         deleted_by_user_id,
#         event_id,
#     )
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependancies.auth import require_role
from app.enum.event_status import EventStatus
from app.enum.user_role import UserRole
from app.models.user import User
from app.schemas.event_management import (
    EventCreateRequest,
    EventListResponse,
    EventManagementItem,
    EventUpdateRequest,
)
from app.services.event_management import (
    EventDeletionConflictError,
    EventNotFoundError,
    InvalidEventScheduleError,
    create_event,
    delete_event,
    get_event,
    list_events,
    update_event,
)


router = APIRouter(prefix="/admin/events", tags=["super-admin-events"])
require_super_admin = require_role(UserRole.SUPER_ADMIN)


@router.get("", response_model=EventListResponse)
def get_events(
    q: str | None = Query(default=None, max_length=255),
    event_status: EventStatus | None = Query(default=None, alias="status"),
    sort_by: Literal["created_at", "name", "entry_open_at"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_super_admin),
):
    return list_events(
        db,
        search=q,
        event_status=event_status,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=EventManagementItem,
    status_code=status.HTTP_201_CREATED,
)
def add_event(
    payload: EventCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    try:
        return create_event(
            db,
            name=payload.name,
            entry_open_at=payload.entry_open_at,
            entry_close_at=payload.entry_close_at,
            exit_open_at=payload.exit_open_at,
            exit_close_at=payload.exit_close_at,
            event_status=payload.status,
            created_by_user_id=current_user.id,
        )
    except InvalidEventScheduleError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("/{event_id}", response_model=EventManagementItem)
def get_event_details(
    event_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_super_admin),
):
    try:
        return get_event(db, event_id=event_id)
    except EventNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch("/{event_id}", response_model=EventManagementItem)
def edit_event(
    payload: EventUpdateRequest,
    event_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    try:
        return update_event(
            db,
            event_id=event_id,
            name=payload.name,
            entry_open_at=payload.entry_open_at,
            entry_close_at=payload.entry_close_at,
            exit_open_at=payload.exit_open_at,
            exit_close_at=payload.exit_close_at,
            event_status=payload.status,
            updated_by_user_id=current_user.id,
        )
    except EventNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidEventScheduleError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_event(
    event_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    try:
        delete_event(
            db,
            event_id=event_id,
            deleted_by_user_id=current_user.id,
        )
    except EventNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except EventDeletionConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)