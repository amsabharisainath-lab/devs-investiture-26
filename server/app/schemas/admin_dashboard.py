from datetime import datetime

from pydantic import BaseModel

from app.enum.event_status import EventStatus


class AdminEventSummary(BaseModel):
    id: int
    name: str
    status: EventStatus
    entry_open_at: datetime
    entry_close_at: datetime
    exit_open_at: datetime
    exit_close_at: datetime


class AdminDashboardCounts(BaseModel):
    registered: int
    present: int
    absent_or_unverified: int
    forgery: int
    entered: int
    exited: int
    currently_inside: int


class AdminDashboardResponse(BaseModel):
    event: AdminEventSummary
    counts: AdminDashboardCounts
