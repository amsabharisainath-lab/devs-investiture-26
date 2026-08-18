import enum

class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    CHECKER = "CHECKER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"