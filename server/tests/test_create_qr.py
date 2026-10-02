from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.orm import Session

from app.dependancies.create_qr import create_qr
from app.enum.attendance_status import AttendanceStatus
from app.enum.event_status import EventStatus
from app.enum.registration_status import RegistrationStatus
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.qr_token import QRToken
from app.models.registration import Registration


class TestCreateQRToken:
    """Test suite for entry and exit QR code issuance logic."""

    def test_invalid_action_returns_400(self, db_session: Session, sample_registration: Registration):
        """Action other than ENTRY or EXIT must return 400."""
        result, status_code = create_qr(sample_registration.id, "INVALID_ACTION", db_session)
        assert status_code == 400
        assert "Invalid action" in result["error"]

    def test_nonexistent_registration_returns_404(self, db_session: Session):
        """Non-existent registration id returns 404."""
        result, status_code = create_qr(999999, "ENTRY", db_session)
        assert status_code == 404
        assert "Registration not found" in result["error"]

    def test_missing_attendance_record_returns_404(
        self, db_session: Session, sample_registration: Registration
    ):
        """Registration without an initialized Attendance record returns 404."""
        # sample_registration has no attendance created yet
        result, status_code = create_qr(sample_registration.id, "ENTRY", db_session)
        assert status_code == 404
        assert "Attendance record not found" in result["error"]

    def test_unconfirmed_registration_returns_403(
        self, db_session: Session, sample_registration: Registration, sample_attendance: Attendance
    ):
        """Cancelled or unconfirmed registration cannot generate QR."""
        sample_registration.status = RegistrationStatus.CANCELLED
        db_session.commit()

        result, status_code = create_qr(sample_registration.id, "ENTRY", db_session)
        assert status_code == 403
        assert "not confirmed" in result["error"]

    def test_inactive_event_returns_403(
        self,
        db_session: Session,
        sample_event: Event,
        sample_registration: Registration,
        sample_attendance: Attendance,
    ):
        """Events that are draft, completed, or cancelled cannot issue QRs."""
        sample_event.status = EventStatus.COMPLETED
        db_session.commit()

        result, status_code = create_qr(sample_registration.id, "ENTRY", db_session)
        assert status_code == 403
        assert "Event is not active" in result["error"]

    def test_successful_entry_qr_generation(
        self, db_session: Session, sample_registration: Registration, sample_attendance: Attendance
    ):
        """Valid entry eligible registration generates token successfully."""
        result, status_code = create_qr(sample_registration.id, "ENTRY", db_session)
        assert status_code == 200
        assert "token" in result
        assert result["action"] == "ENTRY"

        # Verify token was persisted in database
        saved_token = (
            db_session.query(QRToken)
            .filter_by(registration_id=sample_registration.id)
            .first()
        )
        assert saved_token is not None
        assert saved_token.consumed_at is None
        assert len(saved_token.token_hash) == 64  # SHA256 hex digest

    def test_duplicate_active_token_returns_409(
        self, db_session: Session, sample_registration: Registration, sample_attendance: Attendance
    ):
        """Attempting to generate a new token while previous active token exists returns 409 Conflict."""
        # First issuance
        res1, code1 = create_qr(sample_registration.id, "ENTRY", db_session)
        assert code1 == 200

        # Immediate second issuance while token is still valid
        res2, code2 = create_qr(sample_registration.id, "ENTRY", db_session)
        assert code2 == 409
        assert "valid QR token already exists" in res2["error"]

    def test_cannot_generate_exit_qr_before_entry_scanned(
        self, db_session: Session, sample_registration: Registration, sample_attendance: Attendance
    ):
        """Student cannot generate EXIT QR when entry_status is still PENDING."""
        result, status_code = create_qr(sample_registration.id, "EXIT", db_session)
        assert status_code == 403
        assert "Cannot generate EXIT QR before successful entry" in result["error"]

    def test_generate_exit_qr_after_entry_scanned(
        self, db_session: Session, sample_registration: Registration, sample_attendance: Attendance
    ):
        """Student can generate EXIT QR once entry_status is SCANNED."""
        sample_attendance.entry_status = AttendanceStatus.SCANNED
        db_session.commit()

        result, status_code = create_qr(sample_registration.id, "EXIT", db_session)
        assert status_code == 200
        assert "token" in result
        assert result["action"] == "EXIT"
