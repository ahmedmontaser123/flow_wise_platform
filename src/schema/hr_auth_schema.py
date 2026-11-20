
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from models.enums.hr_account_status_enum import HRAccountStatus
from models.enums.hr_role_enum import HRRole

from schema.hr_common_schema import PasswordField, _password_rules, clean_name
from schema.hr_company_schema import CompanyCreateRequest


class AdminAccountIn(PasswordField):
    full_name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str | None) -> str | None:
        return clean_name(value)


class AdminRegisterRequest(BaseModel):
    """Creates a company and its single HR Admin in one step."""

    company: CompanyCreateRequest
    admin: AdminAccountIn


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    role: HRRole


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=72)
    new_password: str = Field(..., min_length=8, max_length=72)

    @field_validator("new_password")
    @classmethod
    def check_new_password(cls, value: str) -> str:
        return _password_rules(value)


class HRUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    full_name: str
    email: str
    role: HRRole
    status: HRAccountStatus
