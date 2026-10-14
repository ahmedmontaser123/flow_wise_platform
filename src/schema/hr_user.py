from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

# Shared properties
class HRUserBase(BaseModel):
    company_id: int
    full_name: str
    email: EmailStr

# Properties required when creating an HR User
class HRUserCreate(HRUserBase):
    password: str

# Properties allowed when updating an HR User (all optional)
class HRUserUpdate(BaseModel):
    company_id: Optional[int] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# Properties returned to the client/API response
class HRUserResponse(HRUserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True