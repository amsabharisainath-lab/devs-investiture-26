import enum

class AttendanceStatus(str, enum.Enum):
    PENDING = "PENDING"
    SCANNED = "SCANNED"
    FAILED = "FAILED"

class AttendanceDecision(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    FORGERY = "FORGERY"