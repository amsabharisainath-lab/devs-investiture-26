from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependancies.auth import require_role
from app.enum.attendance_status import AttendanceDecision, AttendanceStatus
from app.enum.registration_status import RegistrationStatus
from app.enum.user_role import UserRole
from app.schemas.admin_registration import (
    AdminRegistrationDetailResponse,
    AdminRegistrationListResponse,
)
from app.services.admin_registrations import (
    get_admin_registration_detail,
    list_admin_registrations,
)


router = APIRouter(
    prefix="/admin/events",
    tags=["admin"],
    dependencies=[
        Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN))
    ],
)


@router.get(
    "/{event_id}/registrations",
    response_model=AdminRegistrationListResponse,
)
def registrations(
    event_id: int = Path(gt=0),
    q: str | None = Query(default=None, max_length=100),
    name: str | None = Query(default=None, max_length=255),
    roll_no: str | None = Query(default=None, max_length=50),
    year: int | None = Query(default=None, ge=1, le=4),
    department: str | None = Query(default=None, max_length=100),
    registration_status: RegistrationStatus | None = None,
    entry_status: AttendanceStatus | None = None,
    exit_status: AttendanceStatus | None = None,
    decision: AttendanceDecision | None = None,
    unverified_only: bool = False,
    forgery_only: bool = False,
    sort_by: Literal["registered_at", "name", "roll_no"] = "registered_at",
    sort_order: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if unverified_only and (decision is not None or forgery_only):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="unverified_only conflicts with decision/forgery_only",
        )
    if (
        forgery_only
        and decision is not None
        and decision != AttendanceDecision.FORGERY
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="forgery_only conflicts with the selected decision",
        )

    result = list_admin_registrations(
        db,
        event_id,
        search=q,
        name=name,
        roll_no=roll_no,
        year=year,
        department=department,
        registration_status=registration_status,
        entry_status=entry_status,
        exit_status=exit_status,
        decision=decision,
        unverified_only=unverified_only,
        forgery_only=forgery_only,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return result


@router.get(
    "/{event_id}/registrations/{registration_id}",
    response_model=AdminRegistrationDetailResponse,
)
def registration_detail(
    event_id: int = Path(gt=0),
    registration_id: int = Path(gt=0),
    db: Session = Depends(get_db),
):
    result = get_admin_registration_detail(
        db,
        event_id,
        registration_id,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found for this event",
        )
    return result
