from datetime import datetime

from pydantic import BaseModel

from app.enum.attendance_status import AttendanceDecision, AttendanceStatus
from app.enum.qr_action import QRAction
from app.enum.registration_source import RegistrationSource
from app.enum.registration_status import RegistrationStatus
from app.enum.scan_result import ScanResult


class AdminStudentSummary(BaseModel):
    id: int
    name: str
    email: str
    roll_no: str | None
    department: str | None
    year: int | None


class AdminRegistrationItem(BaseModel):
    registration_id: int
    student: AdminStudentSummary
    registration_status: RegistrationStatus
    registration_source: RegistrationSource
    registered_at: datetime
    entry_status: AttendanceStatus | None
    exit_status: AttendanceStatus | None
    decision: AttendanceDecision | None
    entry_at: datetime | None
    exit_at: datetime | None


class AdminPagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class AdminRegistrationListResponse(BaseModel):
    items: list[AdminRegistrationItem]
    pagination: AdminPagination


class AdminAttendanceDetail(BaseModel):
    id: int
    entry_status: AttendanceStatus
    exit_status: AttendanceStatus
    decision: AttendanceDecision | None
    verified_by: int | None
    station_id: int | None
    station_name: str | None
    entry_at: datetime | None
    exit_at: datetime | None
    verified_at: datetime | None
    reason: str | None


class AdminScanHistoryItem(BaseModel):
    id: int
    token_id: int | None
    action: QRAction
    result: ScanResult
    reason: str | None
    actor_id: int | None
    actor_name: str | None
    station_id: int | None
    station_name: str | None
    receipt_at: datetime


class AdminRegistrationDetailResponse(BaseModel):
    registration: AdminRegistrationItem
    attendance: AdminAttendanceDetail | None
    scan_history: list[AdminScanHistoryItem]
    scan_history_total: int
