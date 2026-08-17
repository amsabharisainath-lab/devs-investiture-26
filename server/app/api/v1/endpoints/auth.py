from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.db.session import get_db
from app.dependancies.auth import get_current_user_optional
from app.models.users import User
from app.schemas.auth import MeResponse, SessionUser, TokenResponse
from app.services.auth import (
    verify_institutional_email,
    get_or_create_user,
    create_access_token,
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
    access_token = create_access_token(user=user)

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=MeResponse)
def me(user: User | None = Depends(get_current_user_optional)):
    if not user:
        return MeResponse(authenticated=False, user=None)
    return MeResponse(authenticated=True, user=SessionUser.model_validate(user))