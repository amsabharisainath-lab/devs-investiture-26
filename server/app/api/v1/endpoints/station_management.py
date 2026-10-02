from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependancies.auth import require_role
from app.enum.station_type import StationType
from app.enum.user_role import UserRole
from app.models.user import User
from app.schemas.station_management import (
    StationAssignmentRequest,
    StationCreateRequest,
    StationItem,
    StationListResponse,
    StationUpdateRequest,
)
from app.services.station_management import (
    AssigneeNotFoundError,
    InvalidStationAssigneeError,
    StationNameConflictError,
    StationNotFoundError,
    create_station,
    list_stations,
    set_station_assignment,
    update_station,
)


router = APIRouter(prefix="/admin/stations", tags=["super-admin"])
require_super_admin = require_role(UserRole.SUPER_ADMIN)


@router.get("", response_model=StationListResponse)
def get_stations(
    q: str | None = Query(default=None, max_length=255),
    station_type: StationType | None = Query(default=None, alias="type"),
    active: bool | None = Query(default=None),
    assigned: bool | None = Query(default=None),
    assigned_admin_id: int | None = Query(default=None, gt=0),
    sort_by: Literal["created_at", "name"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_super_admin),
):
    return list_stations(
        db,
        search=q,
        station_type=station_type,
        active=active,
        assigned=assigned,
        assigned_admin_id=assigned_admin_id,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=StationItem, status_code=status.HTTP_201_CREATED)
def add_station(
    payload: StationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    try:
        return create_station(
            db,
            name=payload.name,
            station_type=payload.type,
            active=payload.active,
            created_by_user_id=current_user.id,
        )
    except StationNameConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.patch("/{station_id}", response_model=StationItem)
def edit_station(
    payload: StationUpdateRequest,
    station_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    try:
        return update_station(
            db,
            station_id=station_id,
            name=payload.name,
            station_type=payload.type,
            active=payload.active,
            updated_by_user_id=current_user.id,
        )
    except StationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except StationNameConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.put("/{station_id}/assignment", response_model=StationItem)
def change_station_assignment(
    payload: StationAssignmentRequest,
    station_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    try:
        return set_station_assignment(
            db,
            station_id=station_id,
            assigned_admin_id=payload.assigned_admin_id,
            changed_by_user_id=current_user.id,
        )
    except (StationNotFoundError, AssigneeNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidStationAssigneeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
