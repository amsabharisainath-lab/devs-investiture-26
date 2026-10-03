from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.enum.station_type import StationType
from app.enum.user_role import UserRole


class StationAssigneeSummary(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    is_active: bool


class StationItem(BaseModel):
    id: int
    name: str
    type: StationType
    active: bool
    assigned_admin: StationAssigneeSummary | None
    created_at: datetime
    updated_at: datetime


class StationListPagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class StationListResponse(BaseModel):
    items: list[StationItem]
    pagination: StationListPagination


class StationCreateRequest(BaseModel):
    name: str = Field(max_length=255)
    type: StationType
    active: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Station name cannot be empty")
        return value


class StationUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    type: StationType | None = None
    active: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Station name cannot be empty")
        return value

    @model_validator(mode="after")
    def require_a_change(self):
        if self.name is None and self.type is None and self.active is None:
            raise ValueError("At least one station field must be provided")
        return self


class StationAssignmentRequest(BaseModel):
    # Send null to remove the current assignment.
    # No default is used: an empty body must not accidentally unassign someone.
    assigned_admin_id: int | None = Field(gt=0)
