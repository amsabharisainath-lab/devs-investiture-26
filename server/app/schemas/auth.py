from pydantic import BaseModel, ConfigDict

from app.enum.user_role import UserRole

class SessionUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : int 
    email : str
    name : str
    role : UserRole
    roll_no : str | None = None
    department : str | None = None
    year : int | None = None
    is_active : bool


class MeResponse(BaseModel):
    authenticated : bool
    user : SessionUser | None = None