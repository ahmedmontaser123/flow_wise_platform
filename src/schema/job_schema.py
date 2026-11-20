from datetime import datetime
from typing import Any  # تمت الإضافة لدعم نوع البيانات في schema_definition

from pydantic import BaseModel, ConfigDict, Field, model_validator

from models.enums import EmployType, ExperienceLevel, JobStatus
from src.schema.application_schema import ApplicationResponse


class JobCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    location: str | None = Field(None, min_length=1, max_length=255)
    employment_type: EmployType
    experience_level: ExperienceLevel | None = None
    status: JobStatus = JobStatus.DRAFT
    created_by: int = Field(..., gt=0)
    # الحقول الجديدة تمت إضافتها هنا بالترتيب المطلوب
    schema_definition: dict[str, Any] = Field(..., description="JSONB structure for requirements and LLM parsing")
    weight: float = Field(default=1.0) # التعديل الأول: int إلى float


class JobUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1)
    location: str | None = Field(None, min_length=1, max_length=255)
    employment_type: EmployType | None = None
    experience_level: ExperienceLevel | None = None
    status: JobStatus | None = None
    # إضافة الحقول الجديدة للتحديث
    schema_definition: dict[str, Any] | None = None
    weight: float | None = Field(None) # التعديل الثاني: int إلى float

    @model_validator(mode="after")
    def validate_non_nullable_fields(self):
        non_nullable_fields = (
            "title",
            "description",
            "employment_type",
            "status",
            "schema_definition",  # تمت الإضافة لمنع إرسال قيمة null
            "weight",             # (تبقى كما هي لأنها مجرد نص للتحقق)
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
    schema_definition: dict[str, Any]
    weight: float # التعديل الثالث: int إلى float
    created_at: datetime
    updated_at: datetime

class JobWithApplicationsResponse(JobResponse):
    applications: list[ApplicationResponse] = []