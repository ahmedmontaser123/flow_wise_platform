from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from models.enums import EmployType, ExperienceLevel, JobStatus


class JobCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    location: str | None = Field(None, min_length=1, max_length=255)
    employment_type: EmployType
    experience_level: ExperienceLevel | None = None
    status: JobStatus = JobStatus.DRAFT
    created_by: int = Field(..., gt=0)


class JobUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1)
    location: str | None = Field(None, min_length=1, max_length=255)
    employment_type: EmployType | None = None
    experience_level: ExperienceLevel | None = None
    status: JobStatus | None = None

    @model_validator(mode="after")
    def validate_non_nullable_fields(self):
        non_nullable_fields = (
            "title",
            "description",
            "employment_type",
            "status",
        )

        for field_name in non_nullable_fields:
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(f"{field_name} cannot be null.")

        return self


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    location: str | None
    employment_type: EmployType
    experience_level: ExperienceLevel | None
    status: JobStatus
    created_by: int
    created_at: datetime
    updated_at: datetime