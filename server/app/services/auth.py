from datetime import timedelta, timezone, datetime
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.models.users import User


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


def create_access_token(*, user: User) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user.id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except (ExpiredSignatureError, InvalidTokenError):
        raise ValueError("Invalid or expired token")

    if payload.get("type") != "access" or not payload.get("sub"):
        raise ValueError("Invalid token")

    return payload