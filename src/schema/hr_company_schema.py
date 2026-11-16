from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from schema.hr_common_schema import clean_name


class CompanyCreateRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=150)
    description: str | None = None
    address: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None

    @field_validator("company_name")
    @classmethod
    def normalize_company_name(cls, value: str | None) -> str | None:
        return clean_name(value)


class CompanyUpdateRequest(BaseModel):
    """Only the fields you send are changed."""

    company_name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = None
    address: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None

    @field_validator("company_name")
    @classmethod
    def normalize_company_name(cls, value: str | None) -> str | None:
        return clean_name(value)


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_name: str
    description: str | None
    address: str | None
    phone: str | None
    email: str | None
