import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.enum.user_role import UserRole
from app.models.user import User
from app.models.onspot_registration import OnSpotRegistration
from app.services.auth import (
    DomainNotAllowedError,
    create_access_token,
    decode_access_token,
    get_or_create_user,
    verify_institutional_email,
)


class TestInstitutionalEmailVerification:
    """Test suite for institutional email domain validation."""

    def test_valid_institutional_email_passes(self):
        """Accepted domain with verified email must pass without exception."""
        # Should not raise
        verify_institutional_email("student2026@rajalakshmi.edu.in", email_verified=True)

    def test_case_insensitive_institutional_email_passes(self):
        """Email matching domain in different casing must pass."""
        verify_institutional_email("STUDENT@RAJALAKSHMI.EDU.IN", email_verified=True)

    def test_unverified_email_raises_domain_not_allowed(self):
        """Even with correct domain, unverified email must be rejected."""
        with pytest.raises(DomainNotAllowedError):
            verify_institutional_email("student@rajalakshmi.edu.in", email_verified=False)

    def test_unauthorized_external_domain_rejected(self):
        """Personal or external email domains (e.g. gmail.com) must be rejected."""
        with pytest.raises(DomainNotAllowedError):
            verify_institutional_email("hacker@gmail.com", email_verified=True)

        with pytest.raises(DomainNotAllowedError):
            verify_institutional_email("user@yahoo.com", email_verified=True)

    def test_malformed_email_rejected(self):
        """Emails without @ or missing domain must be rejected."""
        with pytest.raises(DomainNotAllowedError):
            verify_institutional_email("invalid-email-address", email_verified=True)


class TestJWTTokenOperations:
    """Test suite for JWT access token generation and verification."""

    def test_create_and_decode_valid_access_token(self, sample_student: User):
        """A valid token must encode the user id and decode back correctly."""
        token = create_access_token(user=sample_student)
        assert isinstance(token, str)
        assert len(token) > 20

        payload = decode_access_token(token)
        assert payload["sub"] == str(sample_student.id)
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_decode_invalid_tampered_token_raises_error(self):
        """A tampered token string must raise ValueError."""
        with pytest.raises(ValueError, match="Invalid"):
            decode_access_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.tampered.signature")

    def test_decode_garbage_string_raises_error(self):
        """Random string should raise ValueError."""
        with pytest.raises(ValueError):
            decode_access_token("this-is-not-a-valid-jwt-token")


class TestGetOrCreateUser:
    """Test suite for user resolution during OAuth authentication."""

    def test_creates_brand_new_user(self, db_session: Session):
        """A first-time user should be created in the database."""
        sub = "unique_google_sub_301"
        email = "brandnew@rajalakshmi.edu.in"
        name = "Brand New Student"

        user = get_or_create_user(db_session, google_sub=sub, email=email, name=name)
        assert user.id is not None
        assert user.google_sub == sub
        assert user.email == email
        assert user.name == name
        assert user.role == UserRole.STUDENT
        assert user.is_active is True

    def test_returns_existing_user_by_google_sub(self, db_session: Session, sample_student: User):
        """Returning user with same google_sub must return existing User row."""
        user = get_or_create_user(
            db_session,
            google_sub=sample_student.google_sub,
            email=sample_student.email,
            name="Updated Name",
        )
        assert user.id == sample_student.id
        assert user.email == sample_student.email

    def test_claims_unclaimed_onspot_registration_by_email(self, db_session: Session):
        """User pre-created on-spot with google_sub=None claims their account upon first Google login."""
        email = "precreated@rajalakshmi.edu.in"
        unclaimed_user = User(
            google_sub=None,
            email=email,
            name="Pre-created Student",
            role=UserRole.STUDENT,
            is_active=True,
        )
        db_session.add(unclaimed_user)
        db_session.commit()
        db_session.refresh(unclaimed_user)

        new_sub = "new_google_sub_for_precreated"
        claimed_user = get_or_create_user(
            db_session,
            google_sub=new_sub,
            email=email,
            name="Pre-created Student Claimed",
        )

        assert claimed_user.id == unclaimed_user.id
        assert claimed_user.google_sub == new_sub

    def test_conflicting_email_with_different_google_sub_raises_409(
        self, db_session: Session, sample_student: User
    ):
        """Attempting to use an email already tied to a different Google sub raises 409 Conflict."""
        with pytest.raises(HTTPException) as exc_info:
            get_or_create_user(
                db_session,
                google_sub="completely_different_sub_999",
                email=sample_student.email,
                name="Imposter",
            )
        assert exc_info.value.status_code == 409
        assert "Account conflict" in exc_info.value.detail

    def test_inactive_user_raises_403(self, db_session: Session):
        """Disabled user account cannot authenticate (raises 403 Forbidden)."""
        disabled_user = User(
            google_sub="disabled_sub_403",
            email="disabled@rajalakshmi.edu.in",
            name="Disabled User",
            is_active=False,
        )
        db_session.add(disabled_user)
        db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            get_or_create_user(
                db_session,
                google_sub=disabled_user.google_sub,
                email=disabled_user.email,
                name="Disabled User",
            )
        assert exc_info.value.status_code == 403
        assert "Account disabled" in exc_info.value.detail
