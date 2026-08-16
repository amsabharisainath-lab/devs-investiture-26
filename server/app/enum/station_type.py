import enum

class StationType(str, enum.Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    EXCEPTION = "EXCEPTION"