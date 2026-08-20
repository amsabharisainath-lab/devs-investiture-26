import secrets
import hashlib
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

# Assuming imports for your models and enums
# from models import Registration, QRToken
from app.enum.registration_status import RegistrationStatus 
from app.enum.event_status import EventStatus 
from app.enum.qr_action import QRAction 
from app.enum.attendance_status import AttendanceStatus

from app.models.qr_token import QRToken
from app.models.registration import Registration

def create_qr(registration_id: int, action_str: str, db_session: Session):
    try:
        action = QRAction[action_str.upper()]
    except KeyError:
        return {"error": "Invalid action. Must be 'ENTRY' or 'EXIT'."}, 400

    now = datetime.now(timezone.utc)

    # 1. Fetch Registration and Relations
    registration = db_session.query(Registration).filter_by(id=registration_id).first()
    if not registration:
        return {"error": "Registration not found."}, 404

    event = registration.event
    attendance = registration.attendance

    if not event:
        return {"error": "Event not found for this registration."}, 404

    if not attendance:
        return {"error": "Attendance record not found."}, 404

    # 2. Global Eligibility Checks
    if registration.status != RegistrationStatus.CONFIRMED:
        return {"error": "Registration is not confirmed."}, 403
    if event.status != EventStatus.ACTIVE:
        return {"error": "Event is not active."}, 403

    # 3. State Machine & Expiry Logic via Attendance
    if action == QRAction.ENTRY:
        if attendance.entry_status != AttendanceStatus.PENDING:
            return {"error": "Entry already completed or not pending."}, 403
        expires_at = event.entry_close_at

    elif action == QRAction.EXIT:
        if attendance.entry_status != AttendanceStatus.SCANNED:
            return {"error": "Cannot generate EXIT QR before successful entry."}, 403
        if attendance.exit_status != AttendanceStatus.PENDING:
            return {"error": "Exit already completed or not pending."}, 403
        expires_at = event.exit_close_at

    if expires_at <= now:
        return {"error": "QR generation window has already closed."}, 403

    # 4. Atomic Invalidation and Creation
    try:
        # Invalidate existing active tokens for this specific action
        existing_tokens = db_session.query(QRToken).filter(
            QRToken.registration_id == registration_id,
            QRToken.action == action,
            QRToken.consumed_at.is_(None),
            QRToken.expires_at > now
        ).all()

        for token in existing_tokens:
            token.expires_at = now

        # Generate and hash new token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()

        new_qr_token = QRToken(
            registration_id=registration_id,
            action=action,
            token_hash=token_hash,
            issued_at=now,
            expires_at=expires_at, 
            consumed_at=None
        )
        
        db_session.add(new_qr_token)
        db_session.commit()

        return {
            "token": raw_token,
            "action": action.name
        }, 200

    except Exception as e:
        db_session.rollback()
        logging.error(f"Error generating QR: {str(e)}")
        return {"error": "Internal server error during QR generation."}, 500