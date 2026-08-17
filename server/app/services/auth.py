from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.models.users import User
from app.models.session import Session as UserSession


class DomainNotAllowedError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


def verify_institutional_email(email: str, email_verified: bool) -> None:
    if not email_verified:
        raise DomainNotAllowedError()
    try:
        domain = email.rsplit("@", 1)[1].lower()
    except IndexError:
        raise DomainNotAllowedError()

    allowed_domains = {d.strip().lower() for d in settings.ALLOWED_EMAIL_DOMAINS if d.strip()}

    if not allowed_domains:
        # Fail closed: a misconfigured/empty allow-list must never mean "allow everyone"
        raise DomainNotAllowedError()

    if domain not in allowed_domains:
        raise DomainNotAllowedError()
    # domain = email.split("@")[-1].lower()
    # if domain != settings.ALLOWED_EMAIL_DOMAINS.lower():
    #     raise DomainNotAllowedError()


def get_or_create_user(db: DBSession, *, google_sub: str, email: str, name: str) -> User:
    user = db.query(User).filter(User.google_sub == google_sub).one_or_none()
    if user:
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
        return user

    existing_email = db.query(User).filter(User.email == email).one_or_none()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account conflict. Contact an administrator.",
        )

    user = User(google_sub=google_sub, email=email, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_session(
    db: DBSession, *, user: User, user_agent: str | None, ip_address: str | None
) -> UserSession:
    session = UserSession(
        user_id=user.id,
        expires_at=UserSession.new_expiry(settings.SESSION_EXPIRE_MINUTES),
        user_agent=user_agent,
        ip_address=ip_address,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def revoke_session(db: DBSession, *, session_id: str) -> None:
    session = db.query(UserSession).filter(UserSession.id == session_id).one_or_none()
    if session and session.revoked_at is None:
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()