from fastapi import APIRouter

from app.api.v1.endpoints import attendance, auth, health, onspot_registration, registration

api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["health"],
)

api_router.include_router(auth.router)
api_router.include_router(registration.router)
api_router.include_router(onspot_registration.router)
api_router.include_router(attendance.router)