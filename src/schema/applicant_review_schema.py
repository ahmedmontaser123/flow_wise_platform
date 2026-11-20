from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from models.enums import ApplicationStatus, ParsingStatus


class CandidateBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    phone: str | None = None
    education: str | None = None
    portfolio: str | None = None


class ApplicantSummaryOut(BaseModel):
    """One row in a posting's applicant list."""

    application_id: int
    job_id: int
    status: ApplicationStatus
    applied_at: datetime
    updated_at: datetime
    candidate: CandidateBrief
    cv_file_id: int


class ApplicantDetailOut(ApplicantSummaryOut):
    job_title: str
    cv_file_path: str
    cv_parsing_status: ParsingStatus | None = None
    cv_parsed_data: Any | None = None
    allowed_next_statuses: list[ApplicationStatus]


class ApplicationStatusUpdateRequest(BaseModel):
    status: ApplicationStatus
