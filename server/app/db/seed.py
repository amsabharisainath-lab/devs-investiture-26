import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.enum.event_status import EventStatus
from app.enum.station_type import StationType
from app.enum.user_role import UserRole
from app.models.event import Event
from app.models.station import Station
from app.models.user import User

logger = logging.getLogger(__name__)


def seed_test_data(db: Session | None = None) -> dict:
    """
    Seeds initial Event, Station, and test accounts for backend development and testing.
    Safe to call multiple times (idempotent).
    """
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        now = datetime.now(timezone.utc)

        # 1. Ensure Active Event
        event = db.query(Event).filter(Event.name == "DEVS Investiture 2026").first()
        if not event:
            event = Event(
                name="DEVS Investiture 2026",
                status=EventStatus.ACTIVE,
                entry_open_at=now - timedelta(hours=2),
                entry_close_at=now + timedelta(hours=12),
                exit_open_at=now + timedelta(hours=12),
                exit_close_at=now + timedelta(days=2),
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            logger.info("Seeded active event: %s (id: %s)", event.name, event.id)

        # 2. Ensure Default Station
        station = db.query(Station).filter(Station.name == "Gate 1 - Main Entrance").first()
        if not station:
            station = Station(
            name="Gate 1 - Main Entrance",
            type=StationType.ENTRY,
            active=True,
            )
            db.add(station)
            db.commit()
            db.refresh(station)
            logger.info("Seeded station: %s (id: %s)", station.name, station.id)

        # 3. Ensure Test Users
        # Student with complete profile
        student = db.query(User).filter(User.email == "student@rajalakshmi.edu.in").first()
        if not student:
            student = User(
                google_sub="test_sub_student_01",
                email="student@rajalakshmi.edu.in",
                name="Kamlesh Student",
                roll_no="210701001",
                department="Computer Science",
                year=2026,
                role=UserRole.STUDENT,
                is_active=True,
            )
            db.add(student)

        # Student with incomplete profile (for testing profile requirement error)
        newbie = db.query(User).filter(User.email == "newstudent@rajalakshmi.edu.in").first()
        if not newbie:
            newbie = User(
                google_sub="test_sub_newbie_01",
                email="newstudent@rajalakshmi.edu.in",
                name="Fresh Student",
                role=UserRole.STUDENT,
                is_active=True,
            )
            db.add(newbie)

        # Checker Admin
        admin = db.query(User).filter(User.email == "checker@rajalakshmi.edu.in").first()
        if not admin:
            admin = User(
                google_sub="test_sub_admin_01",
                email="checker@rajalakshmi.edu.in",
                name="Staff Checker",
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin)

        # Super Admin
        super_admin = db.query(User).filter(User.email == "superadmin@rajalakshmi.edu.in").first()
        if not super_admin:
            super_admin = User(
                google_sub="test_sub_superadmin_01",
                email="superadmin@rajalakshmi.edu.in",
                name="Head SuperAdmin",
                role=UserRole.SUPER_ADMIN,
                is_active=True,
            )
            db.add(super_admin)

        db.commit()

        return {
            "status": "success",
            "event_id": event.id,
            "station_id": station.id,
            "test_accounts": {
                "student": "student@rajalakshmi.edu.in",
                "incomplete_profile_student": "newstudent@rajalakshmi.edu.in",
                "checker_admin": "checker@rajalakshmi.edu.in",
                "super_admin": "superadmin@rajalakshmi.edu.in",
            },
        }
    finally:
        if should_close:
            db.close()