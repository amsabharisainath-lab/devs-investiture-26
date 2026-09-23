from fastapi import APIRouter

<<<<<<< HEAD
from app.api.v1.endpoints import health, auth, registration, onspot_registration
=======
from app.api.v1.endpoints import health, auth, attendance
>>>>>>> 7999d6e27fc5cf30b046d15c789ca1b66da4a7f4

api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["health"],
)

api_router.include_router(auth.router)
api_router.include_router(registration.router)
api_router.include_router(onspot_registration.router)
api_router.include_router(attendance.router)
