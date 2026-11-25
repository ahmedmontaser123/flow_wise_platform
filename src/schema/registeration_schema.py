
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from models.enums.hr_account_status_enum import HRAccountStatus
from models.enums.hr_role_enum import HRRole

from schema import PasswordField
from schema import CompanyCreateRequest


class AdminAccountIn(PasswordField):
    full_name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = value.strip()

        if not all(char.isalpha() or char.isspace() for char in value):
            raise ValueError(
                "Full name must contain letters and spaces only"
            )

        return value

class AdminRegisterRequest(BaseModel):
    """Creates a company and its single HR Admin in one step."""
    company: CompanyCreateRequest
    admin: AdminAccountIn


