from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.db.session import get_db
from app.dependancies.auth import require_role
from app.enum.qr_action import QRAction
from app.enum.user_role import UserRole
from app.models.user import User
from app.schemas.onspot_registration import (
    OnSpotRegistrationRequest,
    OnSpotRegistrationResponse,
    QRCodeResponse,
)
from app.services.onspot_registration import (
    AlreadyRegisteredError,
    EventNotFoundError,
    QRIssuanceFailedError,
    register_onspot,
)
from app.worker.tasks import send_registration_email

router = APIRouter(tags=["admin", "registration"])
logger = logging.getLogger(__name__)


@router.post(
    "/admin/registrations/on-spot",
    response_model=OnSpotRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def onspot_registration_endpoint(
    event_id: int,
    payload: OnSpotRegistrationRequest,
    db: DBSession = Depends(get_db),
    admin: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
) -> OnSpotRegistrationResponse:
    try:
        registration, onspot_record, raw_token, expires_at = register_onspot(
            event_id=event_id,
            email=payload.email,
            name=payload.name,
            roll_no=payload.roll_no,
            department=payload.department,
            year=payload.year,
            admin=admin,
            db=db,
        )
    except EventNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )
    except AlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This student is already registered for this event.",
        )
    except QRIssuanceFailedError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.result,
        )

    try:
        send_registration_email.delay(registration.id)
    except Exception:
        logger.exception(
            "Could not enqueue registration email for on-spot registration %s",
            registration.id,
        )

    return OnSpotRegistrationResponse(
        id=registration.id,
        event_id=registration.event_id,
        user_id=registration.user_id,
        status=registration.status,
        registered_at=registration.registered_at,
        submitted_email=onspot_record.submitted_email,
        entry_qr=QRCodeResponse(
            action=QRAction.ENTRY,
            token=raw_token,
            expires_at=expires_at,
        ),
    )