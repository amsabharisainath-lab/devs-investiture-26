from datetime import datetime

from pydantic import BaseModel

from app.enum.qr_action import QRAction
from app.enum.scan_result import ScanResult
from app.enum.station_type import StationType
from app.enum.user_role import UserRole


class ScanHistoryActor(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole


class ScannedStudentSummary(BaseModel):
    id: int
    name: str
    email: str
    roll_no: str | None
    department: str | None
    year: int | None


class ScanHistoryEventSummary(BaseModel):
    id: int
    name: str


class ScanHistoryStationSummary(BaseModel):
    id: int
    name: str
    type: StationType


class AdminScanHistoryItem(BaseModel):
    scan_id: int
    token_id: int | None
    registration_id: int | None
    student: ScannedStudentSummary | None
    event: ScanHistoryEventSummary | None
    station: ScanHistoryStationSummary | None
    action: QRAction
    result: ScanResult
    reason: str | None
    receipt_at: datetime


class ScanHistoryPagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class AdminScanHistoryResponse(BaseModel):
    actor: ScanHistoryActor
    items: list[AdminScanHistoryItem]
    pagination: ScanHistoryPagination
