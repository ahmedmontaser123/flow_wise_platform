"""HR Member only: job titles, postings, applicant review."""
from fastapi import APIRouter, Depends, Query, Response, status

from models.enums import ApplicationStatus, JobStatus

from controllers.hr_member_controller import HRMemberController
from helpers.rbac import CurrentMember, DBSession, require_member
from schema.applicant_review_schema import ApplicantDetailOut, ApplicantSummaryOut, ApplicationStatusUpdateRequest
from schema.job_title_schema import JobTitleCreateRequest, JobTitleOut, JobTitleUpdateRequest
from schema.hr_common_schema import Page
from schema.posting_schema import PostingCreateRequest, PostingOut, PostingUpdateRequest

hr_member_router = APIRouter(
    prefix="/api/v1/hr",
    tags=["HR - Member"],
    dependencies=[Depends(require_member)],
)


# ---------------- job titles ----------------
@hr_member_router.post("/job-titles", response_model=JobTitleOut, status_code=status.HTTP_201_CREATED)
async def create_job_title(data: JobTitleCreateRequest, current: CurrentMember, session: DBSession):
    return await HRMemberController(session).create_job_title(current, data)


@hr_member_router.get("/job-titles", response_model=Page[JobTitleOut])
async def list_job_titles(
    current: CurrentMember,
    session: DBSession,
    search: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await HRMemberController(session).list_job_titles(
        current, search=search, limit=limit, offset=offset
    )


@hr_member_router.get("/job-titles/{title_id}", response_model=JobTitleOut)
async def get_job_title(title_id: int, current: CurrentMember, session: DBSession):
    return await HRMemberController(session).get_job_title(current, title_id)


@hr_member_router.patch("/job-titles/{title_id}", response_model=JobTitleOut)
async def update_job_title(
    title_id: int, data: JobTitleUpdateRequest, current: CurrentMember, session: DBSession
):
    return await HRMemberController(session).update_job_title(current, title_id, data)


@hr_member_router.delete("/job-titles/{title_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_title(title_id: int, current: CurrentMember, session: DBSession):
    await HRMemberController(session).delete_job_title(current, title_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------- postings ----------------
@hr_member_router.post(
    "/postings",
    response_model=PostingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a posting (DRAFT)",
)
async def create_posting(data: PostingCreateRequest, current: CurrentMember, session: DBSession):
    return await HRMemberController(session).create_posting(current, data)


@hr_member_router.get("/postings", response_model=Page[PostingOut])
async def list_postings(
    current: CurrentMember,
    session: DBSession,
    status_filter: JobStatus | None = Query(default=None, alias="status"),
    job_title_id: int | None = None,
    mine: bool = Query(default=False, description="Only postings I created"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await HRMemberController(session).list_postings(
        current.company_id,
        status=status_filter,
        job_title_id=job_title_id,
        created_by=current.id if mine else None,
        limit=limit,
        offset=offset,
    )


@hr_member_router.get("/postings/{job_id}", response_model=PostingOut)
async def get_posting(job_id: int, current: CurrentMember, session: DBSession):
    return await HRMemberController(session).get_posting(current.company_id, job_id)


@hr_member_router.patch("/postings/{job_id}", response_model=PostingOut)
async def update_posting(
    job_id: int, data: PostingUpdateRequest, current: CurrentMember, session: DBSession
):
    return await HRMemberController(session).update_posting(current, job_id, data)


@hr_member_router.post("/postings/{job_id}/open", response_model=PostingOut, summary="Publish a posting")
async def open_posting(job_id: int, current: CurrentMember, session: DBSession):
    return await HRMemberController(session).open_posting(current, job_id)


@hr_member_router.post("/postings/{job_id}/close", response_model=PostingOut)
async def close_posting(job_id: int, current: CurrentMember, session: DBSession):
    return await HRMemberController(session).close_posting(current, job_id)


# ---------------- applicant review ----------------
@hr_member_router.get("/postings/{job_id}/applicants", response_model=Page[ApplicantSummaryOut])
async def list_applicants(
    job_id: int,
    current: CurrentMember,
    session: DBSession,
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await HRMemberController(session).list_applicants(
        current.company_id, job_id, status=status_filter, limit=limit, offset=offset
    )


@hr_member_router.get("/applicants/{application_id}", response_model=ApplicantDetailOut)
async def get_applicant(application_id: int, current: CurrentMember, session: DBSession):
    return await HRMemberController(session).get_applicant(current.company_id, application_id)


@hr_member_router.patch("/applicants/{application_id}/status", response_model=ApplicantDetailOut)
async def update_applicant_status(
    application_id: int,
    data: ApplicationStatusUpdateRequest,
    current: CurrentMember,
    session: DBSession,
):
    return await HRMemberController(session).update_applicant_status(current, application_id, data)
