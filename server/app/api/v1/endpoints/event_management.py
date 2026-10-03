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
