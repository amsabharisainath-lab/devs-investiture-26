from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependancies.auth import require_role
from app.enum.user_role import UserRole
from app.schemas.admin_dashboard import AdminDashboardResponse
from app.services.admin_dashboard import get_admin_dashboard


router = APIRouter(
    prefix="/admin/events",
    tags=["admin"],
    dependencies=[
        Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN))
    ],
)


@router.get("/{event_id}/dashboard", response_model=AdminDashboardResponse)
def dashboard(
    event_id: int = Path(gt=0),
    db: Session = Depends(get_db),
):
    result = get_admin_dashboard(db, event_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return result
