from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.enum.attendance_status import AttendanceDecision, AttendanceStatus
from app.enum.event_status import EventStatus
from app.enum.qr_action import QRAction
from app.enum.registration_source import RegistrationSource
from app.enum.registration_status import RegistrationStatus
from app.enum.station_type import StationType
from app.enum.user_role import UserRole
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.qr_token import QRToken
from app.models.registration import Registration
from app.models.station import Station
from app.models.user import User


class TestORMModels:
    """Test suite verifying database entity definitions, relationships, and constraints."""

    def test_user_creation_and_defaults(self, db_session: Session):
        """User model should properly set defaults for role and is_active."""
        user = User(
            email="model_test@rajalakshmi.edu.in",
            name="Model Tester",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.role == UserRole.STUDENT
        assert user.is_active is True
        assert user.created_at is not None

    def test_user_email_uniqueness(self, db_session: Session):
        """Duplicate emails must raise an IntegrityError."""
        user1 = User(email="unique@rajalakshmi.edu.in", name="User 1")
        user2 = User(email="unique@rajalakshmi.edu.in", name="User 2")
        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_event_creation(self, db_session: Session):
        """Event creation with time bounds and status."""
        now = datetime.now(timezone.utc)
        event = Event(
            name="Symposium 2026",
            status=EventStatus.UPCOMING,
            entry_open_at=now,
            entry_close_at=now + timedelta(hours=2),
            exit_open_at=now + timedelta(hours=2),
            exit_close_at=now + timedelta(hours=6),
        )
        db_session.add(event)
        db_session.commit()
        db_session.refresh(event)

        assert event.id is not None
        assert event.status == EventStatus.UPCOMING

    def test_station_creation(self, db_session: Session):
        """Station properly assigns type and active status."""
        station = Station(
            name="Main Gate A",
            type=StationType.ENTRY,
            active=True,
        )
        db_session.add(station)
        db_session.commit()
        db_session.refresh(station)

        assert station.id is not None
        assert station.type == StationType.ENTRY
        assert station.active is True

    def test_registration_uniqueness_per_event(
        self, db_session: Session, sample_student: User, sample_event: Event
    ):
        """A user cannot register twice for the same event."""
        reg1 = Registration(
            event_id=sample_event.id,
            user_id=sample_student.id,
            status=RegistrationStatus.CONFIRMED,
            registration_source=RegistrationSource.SELF,
        )
        db_session.add(reg1)
        db_session.commit()

        reg2 = Registration(
            event_id=sample_event.id,
            user_id=sample_student.id,
            status=RegistrationStatus.CONFIRMED,
            registration_source=RegistrationSource.SELF,
        )
        db_session.add(reg2)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_attendance_and_decision_tracking(
        self, db_session: Session, sample_registration: Registration, sample_admin: User, sample_station: Station
    ):
        """Attendance records track entry, exit, verifier, and decisions."""
        now = datetime.now(timezone.utc)
        attendance = Attendance(
            registration_id=sample_registration.id,
            entry_status=AttendanceStatus.SCANNED,
            exit_status=AttendanceStatus.SCANNED,
            decision=AttendanceDecision.PRESENT,
            verified_by=sample_admin.id,
            station_id=sample_station.id,
            entry_at=now,
            exit_at=now + timedelta(hours=3),
            verified_at=now,
            reason="Verified with valid student ID",
        )
        db_session.add(attendance)
        db_session.commit()
        db_session.refresh(attendance)

        assert attendance.id is not None
        assert attendance.decision == AttendanceDecision.PRESENT
        assert attendance.verified_by == sample_admin.id
        assert attendance.station_id == sample_station.id

    def test_qr_token_attributes(self, db_session: Session, sample_registration: Registration):
        """QRToken tracks action, hash, issued_at, expires_at, and consumed_at."""
        now = datetime.now(timezone.utc)
        token = QRToken(
            registration_id=sample_registration.id,
            action=QRAction.ENTRY,
            token_hash="a" * 64,
            issued_at=now,
            expires_at=now + timedelta(minutes=5),
            consumed_at=None,
        )
        db_session.add(token)
        db_session.commit()
        db_session.refresh(token)

        assert token.id is not None
        assert token.action == QRAction.ENTRY
        assert token.consumed_at is None
