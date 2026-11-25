from pydantic import BaseModel
from models.enums.hr_role_enum import HRRole

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    role: HRRole