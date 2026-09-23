from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependancies.auth import require_role

from app.models.user import User

from app.enum.user_role import UserRole

from app.services.consume_entry_qr import consume_entry_qr
from app.services.verify_entry_qr_details import verify_entry_qr_details
from app.services.verify_exit_and_consume import verify_exit_and_consume

from app.schemas.attendance import (
    AttendanceScanRequest,
    AttendanceVerifyRequest,
)


router = APIRouter(
    prefix="/attendance",
    tags=["attendance"],
)


@router.post("/scan")
def scan(
    request: AttendanceScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.SUPER_ADMIN,
        )
    ),
):
    message, code = verify_entry_qr_details(
        raw_token=request.token,
        db_session=db,
    )

    if code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=code,
            detail=message,
        )

    return message


@router.post("/verify")
def verify(
    request: AttendanceVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.SUPER_ADMIN,
        )
    ),
):
    message, code = consume_entry_qr(
        raw_token=request.token,
        station_id=request.station_id,
        current_user_id=current_user.id,
        db_session=db,
    )

    if code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=code,
            detail=message,
        )

    return message


@router.post("/exit")
def verify_exit(
    request: AttendanceVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(
            UserRole.STUDENT,
            UserRole.ADMIN,
            UserRole.SUPER_ADMIN,
        )
    ),
):
    message, code = verify_exit_and_consume(
        raw_token=request.token,
        current_user_id=current_user.id,
        station_id=request.station_id,
        db_session=db,
    )

    if code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=code,
            detail=message.get(
                "error",
                "Exit verification failed.",
            ),
        )

    return message