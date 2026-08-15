from fastapi import APIRouter, status
from datetime import datetime

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["health"],
    summary="Health Check",
    response_description="Service health status",
)
async def health_check():
    """
    Health check endpoint to verify the service is running.

    Returns:
        dict: Service status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "devs-investiture-api",
    }
