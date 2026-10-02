from fastapi import APIRouter

from app.api.v1.endpoints import attendance, auth, health, onspot_registration, registration, admin_dashboard, admin_registrations, user_management, station_management, admin_scan_history

api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["health"],
)

api_router.include_router(auth.router)
api_router.include_router(registration.router)
api_router.include_router(onspot_registration.router)
api_router.include_router(attendance.router)
api_router.include_router(admin_dashboard.router)
api_router.include_router(admin_registrations.router)
api_router.include_router(user_management.router)
api_router.include_router(station_management.router)
api_router.include_router(admin_scan_history.router)
