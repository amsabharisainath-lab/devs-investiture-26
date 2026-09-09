from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

from app.enum.registration_status import RegistrationStatus
from app.enum.qr_action import QRAction


class OnSpotRegistrationRequest(BaseModel):
    # EmailStr enforces well-formed email syntax only —
    # deliberately no domain restriction here, personal emails
    # (e.g. first-years without institutional accounts yet) are
    # explicitly allowed at on-spot registration.
    email: EmailStr

    name: str
    roll_no: str
    department: str
    year: int

    @field_validator("name", "roll_no", "department")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be blank")
        return v.strip()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class QRCodeResponse(BaseModel):
    action: QRAction
    token: str
    expires_at: datetime | None = None


class OnSpotRegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    user_id: int
    status: RegistrationStatus
    registered_at: datetime
    submitted_email: str
    entry_qr: QRCodeResponse
    message: str = "On-spot registration successful."