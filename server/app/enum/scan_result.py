import enum

class ScanResult(str, enum.Enum):
    VALID = "VALID"
    DUPLICATE = "DUPLICATE"
    EXPIRED = "EXPIRED"
    INVALID = "INVALID"
    FORGERY = "FORGERY"