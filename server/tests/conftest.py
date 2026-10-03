import os
from datetime import datetime, timedelta, timezone
from typing import Generator

# Configure test environment variables before importing application modules
os.environ["DATABASE_URI"] = "sqlite:///./test_devs.db"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["REDIS_URL"] = "memory://"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-execution-only-32char"
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "false"
os.environ["ALLOWED_EMAIL_DOMAINS"] = '["rajalakshmi.edu.in"]'

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.enum.attendance_status import AttendanceStatus
from app.enum.event_status import EventStatus
from app.enum.registration_source import RegistrationSource
from app.enum.registration_status import RegistrationStatus
from app.enum.station_type import StationType
from app.enum.user_role import UserRole
from app.models import Attendance, Event, Registration, Station, User
from app.services.auth import create_access_token
from main import app

# Test SQLite Engine with StaticPool for in-memory or single file testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all database tables before test session and drop after."""
    import app.models  # Ensure all models are registered on Base.metadata

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Clean up test sqlite file if created
    if os.path.exists("./test_devs.db"):
        try:
            os.remove("./test_devs.db")
        except OSError:
            pass


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Yields a database session that rolls back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provides a FastAPI TestClient configured to use the test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_student(db_session: Session) -> User:
    """Creates a sample student user in the database."""
    student = User(
        google_sub="test_student_sub_101",
        email="student.test@rajalakshmi.edu.in",
        name="Test Student",
        roll_no="210701099",
        department="Computer Science",
        year=2026,
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def sample_admin(db_session: Session) -> User:
    """Creates a sample admin user in the database."""
    admin = User(
        google_sub="test_admin_sub_201",
        email="admin.test@rajalakshmi.edu.in",
        name="Test Admin Checker",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def sample_event(db_session: Session) -> Event:
    """Creates an active test event with valid entry and exit timing windows."""
    now = datetime.now(timezone.utc)
    event = Event(
        name="DEVS Pytest Investiture 2026",
        status=EventStatus.ACTIVE,
        entry_open_at=now - timedelta(hours=1),
        entry_close_at=now + timedelta(hours=4),
        exit_open_at=now + timedelta(hours=4),
        exit_close_at=now + timedelta(hours=8),
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


@pytest.fixture
def sample_station(db_session: Session) -> Station:
    """Creates a test scanner station."""
    station = Station(
        name="North Gate Station 1",
        type=StationType.ENTRY,
        active=True,
    )
    db_session.add(station)
    db_session.commit()
    db_session.refresh(station)
    return station


@pytest.fixture
def sample_registration(db_session: Session, sample_student: User, sample_event: Event) -> Registration:
    """Creates a confirmed event registration for the test student."""
    reg = Registration(
        event_id=sample_event.id,
        user_id=sample_student.id,
        status=RegistrationStatus.CONFIRMED,
        registration_source=RegistrationSource.SELF,
    )
    db_session.add(reg)
    db_session.commit()
    db_session.refresh(reg)
    return reg


@pytest.fixture
def sample_attendance(db_session: Session, sample_registration: Registration) -> Attendance:
    """Creates an attendance record with PENDING entry status."""
    att = Attendance(
        registration_id=sample_registration.id,
        entry_status=AttendanceStatus.PENDING,
        exit_status=AttendanceStatus.PENDING,
    )
    db_session.add(att)
    db_session.commit()
    db_session.refresh(att)
    return att


@pytest.fixture
def student_token(sample_student: User) -> str:
    """Generates a valid JWT access token for the sample student."""
    return create_access_token(user=sample_student)


@pytest.fixture
def admin_token(sample_admin: User) -> str:
    """Generates a valid JWT access token for the sample admin."""
    return create_access_token(user=sample_admin)


@pytest.fixture
def student_auth_headers(student_token: str) -> dict:
    """Returns Authorization header with student token."""
    return {"Authorization": f"Bearer {student_token}"}


@pytest.fixture
def admin_auth_headers(admin_token: str) -> dict:
    """Returns Authorization header with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}
