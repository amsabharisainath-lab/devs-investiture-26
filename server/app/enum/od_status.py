import enum

class ODStatus(str, enum.Enum):
    PENDING = "PENDING"
    GENERATED = "GENERATED"
    SENT = "SENT"
    REVOKED = "REVOKED"