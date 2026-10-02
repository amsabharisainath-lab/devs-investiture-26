import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.enum.user_role import UserRole
from app.models.event import Event
from app.models.user import User
from app.services.auth import create_access_token


class TestAuthEndpoints:
    """Test suite for /api/v1/auth endpoints."""

    def test_me_unauthenticated(self, client: TestClient):
        """Calling /auth/me without token returns authenticated=False."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user"] is None

    def test_me_authenticated(
        self, client: TestClient, sample_student: User, student_auth_headers: dict
    ):
        """Calling /auth/me with valid Bearer token returns authenticated=True and user data."""
        response = client.get("/api/v1/auth/me", headers=student_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["user"]["email"] == sample_student.email
        assert data["user"]["role"] == "STUDENT"

    def test_complete_profile_success(self, client: TestClient, db_session: Session):
        """Student with incomplete profile can update and complete it."""
        user = User(
            google_sub="incomplete_student_sub",
            email="incomplete@rajalakshmi.edu.in",
            name="Incomplete Student",
            role=UserRole.STUDENT,
            is_active=True,
            roll_no=None,
            department=None,
            year=None,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        token = create_access_token(user=user)
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "name": "Now Complete Student",
            "roll_no": "210701100",
            "department": "Information Technology",
            "year": 2026,
        }
        response = client.put("/api/v1/auth/profile", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["roll_no"] == "210701100"
        assert data["department"] == "Information Technology"
        assert data["year"] == 2026

    def test_complete_profile_already_completed_raises_409(
        self, client: TestClient, sample_student: User, student_auth_headers: dict
    ):
        """Student whose profile is already complete cannot edit again (returns 409)."""
        payload = {
            "name": "Attempted Change",
            "roll_no": "210701999",
            "department": "Mechanical",
            "year": 2025,
        }
        response = client.put("/api/v1/auth/profile", json=payload, headers=student_auth_headers)
        assert response.status_code == 409
        assert "already been completed" in response.json()["detail"]


class TestRegistrationEndpoints:
    """Test suite for event registration endpoints."""

    def test_register_for_event_requires_auth(self, client: TestClient, sample_event: Event):
        """Unauthenticated call to registration endpoint returns 401."""
        response = client.post(f"/api/v1/events/{sample_event.id}/registration")
        assert response.status_code == 401

    def test_register_for_event_success(
        self, client: TestClient, sample_student: User, sample_event: Event, student_auth_headers: dict
    ):
        """Student with complete profile can successfully register for an active event."""
        response = client.post(
            f"/api/v1/events/{sample_event.id}/registration",
            headers=student_auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["event_id"] == sample_event.id
        assert data["user_id"] == sample_student.id
        assert data["status"] == "CONFIRMED"
        assert "entry_qr" in data
        assert data["entry_qr"]["token"] is not None

    def test_register_for_event_duplicate_raises_409(
        self, client: TestClient, sample_student: User, sample_event: Event, student_auth_headers: dict
    ):
        """Registering again for the same event raises 409 Conflict."""
        # First registration
        r1 = client.post(
            f"/api/v1/events/{sample_event.id}/registration",
            headers=student_auth_headers,
        )
        assert r1.status_code == 201

        # Second registration
        r2 = client.post(
            f"/api/v1/events/{sample_event.id}/registration",
            headers=student_auth_headers,
        )
        assert r2.status_code == 409
        assert "already registered" in r2.json()["detail"]

    def test_register_for_event_incomplete_profile_raises_400(
        self, client: TestClient, db_session: Session, sample_event: Event
    ):
        """Student with missing roll_no/department/year cannot register (returns 400)."""
        incomplete_user = User(
            google_sub="fresh_oauth_student",
            email="fresh@rajalakshmi.edu.in",
            name="Fresh OAuth User",
            role=UserRole.STUDENT,
            is_active=True,
            roll_no=None,
            department=None,
            year=None,
        )
        db_session.add(incomplete_user)
        db_session.commit()
        db_session.refresh(incomplete_user)

        token = create_access_token(user=incomplete_user)
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            f"/api/v1/events/{sample_event.id}/registration",
            headers=headers,
        )
        assert response.status_code == 400
        assert "Complete your user profile" in response.json()["detail"]
