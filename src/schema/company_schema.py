
from pydantic import BaseModel, EmailStr, Field, ConfigDict,field_validator
from typing import Optional


class CompanyCreateRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    address: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(
        default=None,
        min_length=5,
        max_length=20,
        pattern=r"^\+?[0-9]+$"
    )
    email: EmailStr

    @field_validator("company_name")
    @classmethod
    def normalize_company_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = " ".join(value.split())
        if not value:
            raise ValueError("Must not be empty")
        return value
    
class CompanyUpdateRequest(BaseModel):

    company_name: str = Field(..., min_length=2, max_length=150)
    
    description: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=2000
    )
    address: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=255
    )
    phone: Optional[str] = Field(
        default=None,
        min_length=5,
        max_length=20,
        pattern=r"^\+?[0-9]+$"
    )

class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_name: str
    description: str | None
    address: str
    phone: str | None
    email: EmailStr
