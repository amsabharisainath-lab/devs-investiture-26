from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enum.qr_action import QRAction
from app.enum.registration_status import RegistrationStatus

class QRCodeResponse(BaseModel):
    action: QRAction
    token: str  # Frontend converts this raw token into a QR image.
    expires_at: datetime



class RegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    user_id: int
    status: RegistrationStatus
    registered_at: datetime
    message: str = "Successfully registered for the event."
    entry_qr: QRCodeResponse | None = None

class ReissueQRResponse(BaseModel):
    entry_qr: QRCodeResponse
    message: str = "Entry QR reissued."