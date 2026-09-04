from pydantic import BaseModel, Field


class AttendanceScanRequest(BaseModel):
    token: str = Field(..., min_length=1)


class AttendanceVerifyRequest(BaseModel):
    token: str = Field(..., min_length=1)
    station_id: int = Field(..., gt=0)