from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from models.enums import ApplicationStatus, CandidateStatus


class CandidateDashboardApplication(BaseModel):
    id: int
    job_id: int
    job_title: str
    status: ApplicationStatus
    ats_score: float | None = Field(default=None, ge=0, le=100)
    score_breakdown: dict[str, Any] | None = None
    parsed_profile: dict[str, Any] | None = None
    applied_at: datetime
    updated_at: datetime


class CandidateDashboardSummary(BaseModel):
    total_applications: int
    status_counts: dict[str, int]
    yield_ratios: dict[str, float]
    offer_acceptance_rate: float | None


class CandidateDashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    candidate_id: int
    full_name: str
    email: str
    candidate_status: CandidateStatus
    applications: list[CandidateDashboardApplication]
    summary: CandidateDashboardSummary
