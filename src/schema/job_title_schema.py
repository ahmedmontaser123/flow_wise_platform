from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from helpers.hr_utils import clean_name


class JobTitleCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    department: str | None = Field(default=None, max_length=100)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        return clean_name(value)


class JobTitleUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    department: str | None = Field(default=None, max_length=100)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        return clean_name(value)


class JobTitleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int
    name: str
    department: str | None
    description: str | None
    created_by: int | None
    created_at: datetime
    updated_at: datetime
