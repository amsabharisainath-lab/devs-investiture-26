from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.db.session import get_db
from app.dependancies.auth import get_current_user_optional
from app.models.users import User
from app.schemas.auth import MeResponse, SessionUser
from app.services.auth import (
    verify_institutional_email,
    get_or_create_user,
    create_session,
    revoke_session,
)

router = APIRouter(prefix="/auth", tags=["auth"])

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/google/start")
async def google_start(request: Request):
    return await oauth.google.authorize_redirect(request, settings.GOOGLE_REDIRECT_URI, prompt="select_account")


@router.get("/google/callback")
async def google_callback(request: Request, db: DBSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login-error")

    # token = await oauth.google.authorize_access_token(request)
    claims = token.get("userinfo") or await oauth.google.parse_id_token(request, token)

    email = claims["email"]
    email_verified = claims.get("email_verified", False)
    google_sub = claims["sub"]
    name = claims.get("name", email)

    verify_institutional_email(email, email_verified)

    user = get_or_create_user(db, google_sub=google_sub, email=email, name=name)
    session = create_session(
        db,
        user=user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    response = RedirectResponse(url=f"{settings.FRONTEND_URL}/registration")
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session.id,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.SESSION_EXPIRE_MINUTES * 60,
        path="/",
    )
    return response


@router.post("/logout")
def logout(request: Request, db: DBSession = Depends(get_db)):
    session_id = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if session_id:
        revoke_session(db, session_id=session_id)
    response = RedirectResponse(url=f"{settings.FRONTEND_URL}/")
    response.delete_cookie(settings.SESSION_COOKIE_NAME, path="/")
    return response


@router.get("/me", response_model=MeResponse)
def me(user: User | None = Depends(get_current_user_optional)):
    if not user:
        return MeResponse(authenticated=False, user=None)
    return MeResponse(authenticated=True, user=SessionUser.model_validate(user))