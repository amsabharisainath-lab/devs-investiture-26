from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.enum.station_type import StationType
from app.enum.user_role import UserRole


EditableUserRole = Literal["STUDENT", "ADMIN", "SUPER_ADMIN"]


class AssignedStationSummary(BaseModel):
    id: int
    name: str
    type: StationType
    active: bool


class UserManagementItem(BaseModel):
    id: int
    name: str
    email: str
    roll_no: str | None
    department: str | None
    year: int | None
    role: UserRole
    is_active: bool
    assigned_stations: list[AssignedStationSummary]
    created_at: datetime
    updated_at: datetime


class UserListPagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class UserListResponse(BaseModel):
    items: list[UserManagementItem]
    pagination: UserListPagination


class UserRoleUpdateRequest(BaseModel):
    role: EditableUserRole
