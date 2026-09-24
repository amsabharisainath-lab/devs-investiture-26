import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.db.session import get_db
from app.dependancies.auth import get_current_user
from app.dependancies.create_qr import create_qr
from app.enum.qr_action import QRAction
from app.enum.registration_status import RegistrationStatus
from app.models.registration import Registration
from app.models.qr_token import QRToken
from app.models.user import User
from app.schemas.registration import (
    QRCodeResponse,
    RegistrationResponse,
    ReissueQRResponse,
)
from app.services.registration import (
    AlreadyRegisteredError,
    EventNotFoundError,
    ProfileIncompleteError,
    QRIssuanceFailedError,
    StudentRoleRequiredError,
    register_for_event,
)
from app.worker.tasks import send_registration_email

router = APIRouter(tags=["registration"])
logger = logging.getLogger(__name__)


@router.post(
    "/events/{event_id}/registration",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_for_event_endpoint(
    event_id: int,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RegistrationResponse:
    try:
        registration, raw_token, expires_at = register_for_event(
            event_id=event_id,
            user=user,
            db=db,
        )
    except StudentRoleRequiredError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can register for this event.",
        )
    except ProfileIncompleteError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complete your user profile before registering for this event.",
        )
    except EventNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )
    except AlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already registered for this event.",
        )
    except QRIssuanceFailedError as exc:
        # Registration itself succeeded and is already committed.
        # The student is registered but has no QR yet — they should
        # use the reissue endpoint below to retry.
        raise HTTPException(
            status_code=exc.status_code,
            detail=(
                f"Registered, but QR issuance failed: {exc.detail}. "
                "Use /events/{event_id}/registration/entry-qr to retry."
            ),
        )
    try:
        send_registration_email.delay(registration.id)
    except Exception:
        # Registration is already committed. Email delivery is retried by
        # Celery when the broker is available and must not fail this response.
        logger.exception(
            "Could not enqueue registration email for registration %s",
            registration.id,
        )

    return RegistrationResponse(
        id=registration.id,
        event_id=registration.event_id,
        user_id=registration.user_id,
        status=registration.status,
        registered_at=registration.registered_at,
        entry_qr=QRCodeResponse(
            action=QRAction.ENTRY,
            token=raw_token,
            expires_at=expires_at,
        ),
    )


@router.post(
    "/events/{event_id}/registration/entry-qr",
    response_model=ReissueQRResponse,
)
def reissue_entry_qr_endpoint(
    event_id: int,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ReissueQRResponse:
    """
    Fallback for when create_qr failed during registration, or the
    student never received their token. Safe to call repeatedly —
    create_qr's upsert logic only blocks when the token is already
    consumed.
    """
    registration = (
        db.query(Registration)
        .filter(
            Registration.event_id == event_id,
            Registration.user_id == user.id,
            Registration.status == RegistrationStatus.CONFIRMED,
        )
        .first()
    )
    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No confirmed registration found for this event.",
        )

    result, status_code = create_qr(
        registration_id=registration.id,
        action_str="ENTRY",
        db_session=db,
    )

    if status_code != 200:
        raise HTTPException(
            status_code=status_code,
            detail=result.get("error", "QR issuance failed."),
        )

    qr_token = (
        db.query(QRToken)
        .filter(
            QRToken.registration_id == registration.id,
            QRToken.action == QRAction.ENTRY,
        )
        .first()
    )

    return ReissueQRResponse(
        entry_qr=QRCodeResponse(
            action=QRAction.ENTRY,
            token=result["token"],
            expires_at=qr_token.expires_at if qr_token else None,
        )
    )
