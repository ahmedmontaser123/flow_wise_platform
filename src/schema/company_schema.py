
from pydantic import BaseModel, EmailStr
from typing import Optional

# Shared properties
class CompanyBase(BaseModel):
    company_name: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

# Properties required when creating a company
class CompanyCreate(CompanyBase):
    pass

# Properties allowed when updating a company (all optional)
class CompanyUpdate(BaseModel):
    company_name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

# Properties returned to the client/API response
class CompanyResponse(CompanyBase):
    id: int

    class Config:
        from_attributes = True