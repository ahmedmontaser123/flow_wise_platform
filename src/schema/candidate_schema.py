from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict,Field,field_validator
from models.enums import CandidateStatus
from typing import Optional


class CandidateCreateRequest(BaseModel):  # str | None 
    full_name: str = Field(...,min_length=4,max_length = 150)
    email: EmailStr
    phone: Optional[str] = Field(default=None, min_length=5 , max_length=20,pattern=r"^\+?[0-9]+$")
    education: Optional[str] = Field(default=None , min_length=6,max_length=255)
    portfolio: str | None = None


    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:

        if not value:
            raise ValueError("Full name cannot be empty")
        
        value = value.strip()
        if not all(char.isalpha() or char == " " for char in value):
            raise ValueError(
                "Full name must contain letters and spaces only"
            )

        return value

class CandidateUpdateStatus(BaseModel): # page fill data candidate ---> store database 
    model_config = ConfigDict(from_attributes=True)
    status: CandidateStatus | None = None


class CandidateResponse(CandidateCreateRequest):
    created_at: datetime
    status:CandidateStatus | None = None
    model_config = ConfigDict(from_attributes=True)
