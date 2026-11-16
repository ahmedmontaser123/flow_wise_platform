from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.enums import EmployType, ExperienceLevel, JobStatus


class PostingCreateRequest(BaseModel):
    """Creates a posting as DRAFT. Call /open to publish it.

    `title` is optional: if empty, the job title's name is used.
    """

    job_title_id: int
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description: str = Field(..., min_length=10)
    location: str | None = Field(default=None, max_length=255)
    employment_type: EmployType
    experience_level: ExperienceLevel | None = None


class PostingUpdateRequest(BaseModel):
    job_title_id: int | None = None
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, min_length=10)
    location: str | None = Field(default=None, max_length=255)
    employment_type: EmployType | None = None
    experience_level: ExperienceLevel | None = None


class PostingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_title_id: int | None
    title: str
    description: str
    location: str | None
    employment_type: EmployType
    experience_level: ExperienceLevel | None
    status: JobStatus
    created_by: int
    created_at: datetime
    updated_at: datetime
    applicants_count: int = 0
