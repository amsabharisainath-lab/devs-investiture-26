from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependancies.auth import require_role
from app.enum.user_role import UserRole
from app.models.user import User
from app.schemas.user_management import (
    EditableUserRole,
    UserListResponse,
    UserManagementItem,
    UserRoleUpdateRequest,
)
from app.services.user_management import (
    RoleChangeConflictError,
    UserNotFoundError,
    change_user_role,
    list_users,
)


router = APIRouter(prefix="/admin/users", tags=["super-admin"])
require_super_admin = require_role(UserRole.SUPER_ADMIN)


@router.get("", response_model=UserListResponse)
def get_users(
    q: str | None = Query(default=None, max_length=255),
    role: EditableUserRole | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    sort_by: Literal["created_at", "name", "email"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_super_admin),
):
    return list_users(
        db,
        search=q,
        role=UserRole(role) if role is not None else None,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )


@router.patch("/{user_id}/role", response_model=UserManagementItem)
def update_user_role(
    payload: UserRoleUpdateRequest,
    user_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    try:
        return change_user_role(
            db,
            user_id=user_id,
            new_role=UserRole(payload.role),
            changed_by_user_id=current_user.id,
        )
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except RoleChangeConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
