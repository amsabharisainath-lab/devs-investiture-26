from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependancies.auth import require_role
from app.enum.qr_action import QRAction
from app.enum.scan_result import ScanResult
from app.enum.user_role import UserRole
from app.models.user import User
from app.schemas.admin_scan_history import AdminScanHistoryResponse
from app.services.admin_scan_history import (
    ScanActorNotFoundError,
    list_scans_by_actor,
)

router = APIRouter(prefix="/admin", tags=["admin-scan-history"])

require_admin = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
require_super_admin = require_role(UserRole.SUPER_ADMIN)


def _get_scan_history(
    *,
    db: Session,
    actor_id: int,
    q: str | None,
    event_id: int | None,
    station_id: int | None,
    action: QRAction | None,
    result: ScanResult | None,
    date_from: datetime | None,
    date_to: datetime | None,
    page: int,
    page_size: int,
) -> AdminScanHistoryResponse:
    for field_name, value in (("date_from", date_from), ("date_to", date_to)):
        if value is not None and value.utcoffset() is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field_name} must include a timezone",
            )

    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="date_from must be earlier than or equal to date_to",
        )

    try:
        return list_scans_by_actor(
            db,
            actor_id=actor_id,
            search=q,
            event_id=event_id,
            station_id=station_id,
            action=action,
            result=result,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size,
        )
    except ScanActorNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get("/me/scans", response_model=AdminScanHistoryResponse)
def get_my_scan_history(
    q: str | None = Query(default=None, max_length=255),
    event_id: int | None = Query(default=None, gt=0),
    station_id: int | None = Query(default=None, gt=0),
    action: QRAction | None = None,
    result: ScanResult | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return _get_scan_history(
        db=db,
        actor_id=current_user.id,
        q=q,
        event_id=event_id,
        station_id=station_id,
        action=action,
        result=result,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/users/{admin_id}/scans",
    response_model=AdminScanHistoryResponse,
)
def get_user_scan_history(
    admin_id: int = Path(gt=0),
    q: str | None = Query(default=None, max_length=255),
    event_id: int | None = Query(default=None, gt=0),
    station_id: int | None = Query(default=None, gt=0),
    action: QRAction | None = None,
    result: ScanResult | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_super_admin),
):
    return _get_scan_history(
        db=db,
        actor_id=admin_id,
        q=q,
        event_id=event_id,
        station_id=station_id,
        action=action,
        result=result,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
