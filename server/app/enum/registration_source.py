import enum

class RegistrationSource(str, enum.Enum):
    SELF = "SELF"
    ON_SPOT = "ON_SPOT"