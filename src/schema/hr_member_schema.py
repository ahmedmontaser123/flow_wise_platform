from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from models.enums.hr_account_status_enum import HRAccountStatus
from models.enums.hr_role_enum import HRRole

from schema.hr_common_schema import PasswordField, _password_rules, clean_name


class MemberCreateRequest(PasswordField):
    """The admin sets the initial password and shares it with the member."""

    full_name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str | None) -> str | None:
        return clean_name(value)


class MemberUpdateRequest(BaseModel):
    """Only the fields you send are changed. Sending `password` resets it."""

    full_name: str | None = Field(default=None, min_length=3, max_length=100)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=72)

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str | None) -> str | None:
        return clean_name(value)

    @field_validator("password")
    @classmethod
    def check_password(cls, value: str | None) -> str | None:
        return None if value is None else _password_rules(value)


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    full_name: str
    email: str
    role: HRRole
    status: HRAccountStatus
    approved_by_id: int | None = None
    approved_at: datetime | None = None
    created_at: datetime
