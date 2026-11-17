from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.db.connection_database import get_db_session
from models.enums import ApplicationStatus
from repositories.dashboard_repository import DashboardRepository
from schema.dashboard_schema import (
    CandidateDashboardApplication,
    CandidateDashboardResponse,
    CandidateDashboardSummary,
)


dashboard_router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["dashboard"],
)


def _percentage(value: int, total: int) -> float:
    return round(value * 100 / total, 2) if total else 0.0


@dashboard_router.get(
    "/candidates/{candidate_id}",
    response_model=CandidateDashboardResponse,
)
async def get_candidate_dashboard(
    candidate_id: int,
    job_id: int | None = Query(default=None, gt=0),
    session: AsyncSession = Depends(get_db_session),
) -> CandidateDashboardResponse:
    candidate, applications = await DashboardRepository(session).get_candidate_dashboard(
        candidate_id, job_id
    )
    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )

    status_counts = Counter(application.status.value for application in applications)
    total = len(applications)
    received = status_counts.get(ApplicationStatus.RECEIVED.value, 0)
    screened = status_counts.get(ApplicationStatus.SCREENED.value, 0)
    shortlisted = status_counts.get(ApplicationStatus.SHORTLISTED.value, 0)
    interviewed = status_counts.get(ApplicationStatus.INTERVIEW.value, 0)
    offers = status_counts.get(ApplicationStatus.OFFER.value, 0)
    hired = status_counts.get(ApplicationStatus.HIRED.value, 0)

    application_data = [
        CandidateDashboardApplication(
            id=application.id,
            job_id=application.job_id,
            job_title=application.job.title,
            status=application.status,
            ats_score=application.ats_score,
            score_breakdown=application.score_breakdown,
            parsed_profile=(
                application.cv_file.parsed.parsed_data
                if application.cv_file.parsed is not None
                else None
            ),
            applied_at=application.created_at,
            updated_at=application.updated_at,
        )
        for application in applications
    ]

    return CandidateDashboardResponse(
        candidate_id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        candidate_status=candidate.status,
        applications=application_data,
        summary=CandidateDashboardSummary(
            total_applications=total,
            status_counts=dict(status_counts),
            yield_ratios={
                "received_to_screened": _percentage(screened, received),
                "screened_to_shortlisted": _percentage(shortlisted, screened),
                "shortlisted_to_interview": _percentage(interviewed, shortlisted),
                "interview_to_offer": _percentage(offers, interviewed),
                "offer_to_hired": _percentage(hired, offers),
            },
            offer_acceptance_rate=(round(hired * 100 / offers, 2) if offers else None),
        ),
    )
