from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.enum.event_status import EventStatus


def _require_timezone(value: datetime, field_name: str) -> datetime:
    if value.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone")
    return value


def _validate_schedule(
    entry_open_at: datetime,
    entry_close_at: datetime,
    exit_open_at: datetime,
    exit_close_at: datetime,
) -> None:
    if not (
        entry_open_at
        < entry_close_at
        <= exit_open_at
        < exit_close_at
    ):
        raise ValueError(
            "Event times must satisfy: entry_open_at < entry_close_at "
            "<= exit_open_at < exit_close_at"
        )


class EventManagementItem(BaseModel):
    id: int
    name: str
    entry_open_at: datetime
    entry_close_at: datetime
    exit_open_at: datetime
    exit_close_at: datetime
    status: EventStatus
    registration_count: int
    can_delete: bool
    created_at: datetime
    updated_at: datetime


class EventListPagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class EventListResponse(BaseModel):
    items: list[EventManagementItem]
    pagination: EventListPagination


class EventCreateRequest(BaseModel):
    name: str = Field(max_length=255)
    entry_open_at: datetime
    entry_close_at: datetime
    exit_open_at: datetime
    exit_close_at: datetime
    status: EventStatus = EventStatus.UPCOMING

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Event name cannot be empty")
        return value

    @field_validator(
        "entry_open_at",
        "entry_close_at",
        "exit_open_at",
        "exit_close_at",
    )
    @classmethod
    def validate_timezone(cls, value: datetime, info):
        return _require_timezone(value, info.field_name)

    @model_validator(mode="after")
    def validate_event_schedule(self):
        _validate_schedule(
            self.entry_open_at,
            self.entry_close_at,
            self.exit_open_at,
            self.exit_close_at,
        )
        return self


class EventUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    entry_open_at: datetime | None = None
    entry_close_at: datetime | None = None
    exit_open_at: datetime | None = None
    exit_close_at: datetime | None = None
    status: EventStatus | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Event name cannot be empty")
        return value

    @field_validator(
        "entry_open_at",
        "entry_close_at",
        "exit_open_at",
        "exit_close_at",
    )
    @classmethod
    def validate_timezone(
        cls,
        value: datetime | None,
        info,
    ) -> datetime | None:
        if value is None:
            return None
        return _require_timezone(value, info.field_name)

    @model_validator(mode="after")
    def require_a_change(self):
        if all(
            value is None
            for value in (
                self.name,
                self.entry_open_at,
                self.entry_close_at,
                self.exit_open_at,
                self.exit_close_at,
                self.status,
            )
        ):
            raise ValueError("At least one event field must be provided")
        return self
