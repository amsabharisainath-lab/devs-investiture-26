from datetime import timedelta, timezone, datetime
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.models.user import User
from sqlalchemy.orm import Session

from app.models.onspot_registration import OnSpotRegistration


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



# def get_or_create_user(db: DBSession, *, google_sub: str, email: str, name: str) -> User:
#     user = db.query(User).filter(User.google_sub == google_sub).one_or_none()
#     if user:
#         if not user.is_active:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
#         return user
#
#     existing_email = db.query(User).filter(User.email == email).one_or_none()
#     if existing_email:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Account conflict. Contact an administrator.",
#         )
#
#     user = User(google_sub=google_sub, email=email, name=name)
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return user

def get_or_create_user(db: DBSession, *, google_sub: str, email: str, name: str) -> User:
    user = db.query(User).filter(User.google_sub == google_sub).one_or_none()
    if user:
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
        return user

    normalized_email = email.strip().lower()
    existing_email = db.query(User).filter(User.email == normalized_email).one_or_none()

    if existing_email:
        if existing_email.google_sub is None:
            # Unclaimed on-spot registration — attach this sub instead
            # of rejecting. This is the expected first login for
            # anyone the admin pre-registered at the venue.
            existing_email.google_sub = google_sub
            db.commit()
            db.refresh(existing_email)

            onspot_record = (
                db.query(OnSpotRegistration)
                .filter(
                    OnSpotRegistration.user_id == existing_email.id,
                    OnSpotRegistration.claimed_at.is_(None),
                )
                .one_or_none()
            )
            if onspot_record:
                onspot_record.claimed_at = datetime.now(timezone.utc)
                db.commit()

            return existing_email

        # Email exists AND already has a different real sub attached —
        # this is the genuine conflict case the original code was
        # trying to catch. Keep the reject here.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account conflict. Contact an administrator.",
        )

    user = User(google_sub=google_sub, email=normalized_email, name=name)
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

def get_or_link_google_user(
    *,
    google_sub: str,
    email: str,
    db: Session,
) -> User:
    """
    Resolves a Google login to a User row.

    1. If a User already has this exact google_sub, return it
       (normal returning-user login).
    2. Otherwise, look for an existing User by normalized email with
       google_sub IS NULL — this is an on-spot-created row waiting to
       be claimed. Attach the sub to that SAME row instead of creating
       a new one.
    3. Otherwise, no existing record at all — create a fresh User.

    This must run BEFORE any "create new user" logic in the callback,
    regardless of whether the domain check passed or failed.
    """
    normalized_email = email.strip().lower()

    # Step 1: match by sub — already a known, logged-in-before user.
    existing_by_sub = (
        db.query(User).filter(User.google_sub == google_sub).one_or_none()
    )
    if existing_by_sub:
        return existing_by_sub

    # Step 2: match by email, only if that row has never been claimed.
    unclaimed_by_email = (
        db.query(User)
        .filter(User.email == normalized_email, User.google_sub.is_(None))
        .one_or_none()
    )
    if unclaimed_by_email:
        unclaimed_by_email.google_sub = google_sub
        db.commit()
        db.refresh(unclaimed_by_email)

        # Mark the on-spot record as claimed, if one exists.

        onspot_record = (
            db.query(OnSpotRegistration)
            .filter(OnSpotRegistration.user_id == unclaimed_by_email.id)
            .filter(OnSpotRegistration.claimed_at.is_(None))
            .one_or_none()
        )
        if onspot_record:
            onspot_record.claimed_at = datetime.now(timezone.utc)
            db.commit()

        return unclaimed_by_email

    # Step 3: genuinely new person — no existing row at all.
    new_user = User(
        google_sub=google_sub,
        email=normalized_email,
        # name/role/etc. — however your existing creation path sets these
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user