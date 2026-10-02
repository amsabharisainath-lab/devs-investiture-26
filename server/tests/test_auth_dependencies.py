import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.dependancies.auth import get_current_user, get_current_user_optional, require_role
from app.enum.user_role import UserRole
from app.models.user import User
from app.services.auth import create_access_token


class TestAuthDependencies:
    """Test suite for FastAPI dependency injection auth handlers."""

    def test_get_current_user_missing_credentials_raises_401(self, db_session: Session):
        """Calling get_current_user without credentials raises 401."""
        with pytest.raises(HTTPException) as exc:
            get_current_user(credentials=None, db=db_session)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == "Not authenticated"

    def test_get_current_user_non_bearer_scheme_raises_401(self, db_session: Session):
        """Credentials scheme other than 'Bearer' raises 401."""
        creds = HTTPAuthorizationCredentials(scheme="Basic", credentials="dGVzdDp0ZXN0")
        with pytest.raises(HTTPException) as exc:
            get_current_user(credentials=creds, db=db_session)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token_raises_401(self, db_session: Session):
        """Invalid JWT string raises 401."""
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad.token.signature")
        with pytest.raises(HTTPException) as exc:
            get_current_user(credentials=creds, db=db_session)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_valid_token_returns_user(
        self, db_session: Session, sample_student: User
    ):
        """Valid bearer token resolves to the active user entity."""
        token = create_access_token(user=sample_student)
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        user = get_current_user(credentials=creds, db=db_session)
        assert user.id == sample_student.id
        assert user.email == sample_student.email

    def test_get_current_user_inactive_user_raises_401(
        self, db_session: Session, sample_student: User
    ):
        """If user is deactivated in database, valid token still raises 401."""
        token = create_access_token(user=sample_student)
        sample_student.is_active = False
        db_session.commit()

        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with pytest.raises(HTTPException) as exc:
            get_current_user(credentials=creds, db=db_session)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_optional_returns_none_when_unauthenticated(self, db_session: Session):
        """Optional user dependency returns None instead of raising."""
        result = get_current_user_optional(credentials=None, db=db_session)
        assert result is None

    def test_get_current_user_optional_returns_user_when_valid(
        self, db_session: Session, sample_student: User
    ):
        """Optional user dependency returns User when token is valid."""
        token = create_access_token(user=sample_student)
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        result = get_current_user_optional(credentials=creds, db=db_session)
        assert result is not None
        assert result.id == sample_student.id

    def test_require_role_permits_authorized_role(self, sample_admin: User):
        """require_role passes when user role matches allowed roles."""
        admin_guard = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
        authorized_user = admin_guard(user=sample_admin)
        assert authorized_user.id == sample_admin.id

    def test_require_role_forbids_unauthorized_role(self, sample_student: User):
        """require_role raises 403 when user role is not in allowed list."""
        admin_guard = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
        with pytest.raises(HTTPException) as exc:
            admin_guard(user=sample_student)
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc.value.detail == "Forbidden"
