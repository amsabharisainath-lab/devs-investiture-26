import hashlib
from datetime import datetime, timezone
from sqlalchemy.orm import Session

# Assuming these are your model and enum imports:
# from models import QRToken, ScanEvent
# from enums import QRAction, ScanResult, AttendanceStatus
from app.models.qr_token import QRToken

from app.enum.qr_action import QRAction
from app.enum.attendance_status import AttendanceStatus

def verify_entry_qr_details(raw_token: str, db_session: Session):
    """
    Step 1 (ENTRY): Verifies an ENTRY QR and returns user details for manual check.
    Does NOT consume the token.
    """
    now = datetime.now(timezone.utc)
    token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()

    # 1. Cryptographic and Token State Check
    qr_token = db_session.query(QRToken).filter_by(token_hash=token_hash).first()
    
    if not qr_token:
        return {"error": "Invalid QR code."}, 403
    if qr_token.action != QRAction.ENTRY:
        return {"error": "Invalid token action. Expected ENTRY."}, 403
    if qr_token.consumed_at is not None:
        return {"error": "QR code has already been used."}, 403
    if now >= qr_token.expires_at:
        return {"error": "QR code has expired."}, 403

    # 2. Relationship Guards
    registration = qr_token.registration
    if not registration:
        return {"error": "Associated registration not found."}, 404
        
    event = registration.event
    if not event:
        return {"error": "Associated event not found."}, 404
        
    attendance = registration.attendance
    if not attendance:
        return {"error": "Attendance record not found."}, 404
    
    user = registration.user
    if not user:
        return {"error": "User details not found."}, 404

    # 3. Time Window & Sequence Rules
    if not (event.entry_open_at <= now <= event.entry_close_at):
        return {"error": "Outside of event entry window."}, 403
    if attendance.entry_status != AttendanceStatus.PENDING:
        return {"error": "User has already entered."}, 403

    # 4. Return Details for Volunteer Verification
    return {
        "is_valid": True,
        "participant_details": {
            "registration_id": registration.id,
            "name": user.name,
            "email": user.email,
            "roll_no": user.roll_no,
            "department": user.department,
            "year": user.year
        },
        "event_details": {
            "name": event.name
        }
    }, 200