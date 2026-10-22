from datetime import datetime
from pydantic import BaseModel, EmailStr, Field,field_validator,ConfigDict
from typing import Optional


class HRUserCreate(BaseModel):
    company_id: int
    full_name: str = Field(...,min_length=4,max_length = 150)
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=255
    )

    model_config = ConfigDict(from_attributes=True)


class HRUserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None,min_length=7, max_length=100)
    password:Optional[str] = Field(default=None, min_length = 3 , max_length = 255)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        if not value:
            return None 
        value = value.strip() 

        if not all(char.isalpha() or char.isspace() for char in value):
            raise ValueError(
                "Full name must contain letters and spaces only"
            )

        return value


