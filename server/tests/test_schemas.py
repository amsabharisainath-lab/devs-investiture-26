import pytest
from pydantic import ValidationError

from app.enum.user_role import UserRole
from app.schemas.attendance import AttendanceScanRequest, AttendanceVerifyRequest
from app.schemas.auth import CompleteProfileRequest, SessionUser, TokenResponse
from app.schemas.registration import QRCodeResponse, RegistrationResponse
from app.enum.qr_action import QRAction
from app.enum.registration_status import RegistrationStatus
from datetime import datetime, timezone


class TestSchemas:
    """Test suite for Pydantic API boundary validation models."""

    def test_complete_profile_request_valid(self):
        """Valid profile request succeeds."""
        data = {
            "name": "Kamlesh",
            "roll_no": "210701001",
            "department": "Computer Science",
            "year": 2026,
        }
        req = CompleteProfileRequest(**data)
        assert req.name == "Kamlesh"
        assert req.year == 2026

    def test_complete_profile_request_invalid_year(self):
        """Year outside 2000-2100 range must fail validation."""
        with pytest.raises(ValidationError):
            CompleteProfileRequest(
                name="Kamlesh",
                roll_no="210701001",
                department="CSE",
                year=1999,
            )

        with pytest.raises(ValidationError):
            CompleteProfileRequest(
                name="Kamlesh",
                roll_no="210701001",
                department="CSE",
                year=2105,
            )

    def test_complete_profile_request_empty_fields(self):
        """Empty string fields should fail validation."""
        with pytest.raises(ValidationError):
            CompleteProfileRequest(
                name="",
                roll_no="210701001",
                department="CSE",
                year=2026,
            )

    def test_token_response(self):
        """TokenResponse serialization."""
        res = TokenResponse(access_token="sample-jwt", expires_in=1800)
        assert res.token_type == "bearer"
        assert res.access_token == "sample-jwt"
        assert res.expires_in == 1800

    def test_attendance_scan_request(self):
        """AttendanceScanRequest requires non-empty token."""
        req = AttendanceScanRequest(token="test-qr-token")
        assert req.token == "test-qr-token"

        with pytest.raises(ValidationError):
            AttendanceScanRequest(token="")

    def test_attendance_verify_request(self):
        """AttendanceVerifyRequest requires valid positive station_id."""
        req = AttendanceVerifyRequest(token="valid-token", station_id=1)
        assert req.station_id == 1

        with pytest.raises(ValidationError):
            AttendanceVerifyRequest(token="valid-token", station_id=0)

    def test_qr_code_response(self):
        """QRCodeResponse model."""
        now = datetime.now(timezone.utc)
        qr = QRCodeResponse(action=QRAction.ENTRY, token="sample-token", expires_at=now)
        assert qr.action == QRAction.ENTRY
        assert qr.token == "sample-token"
