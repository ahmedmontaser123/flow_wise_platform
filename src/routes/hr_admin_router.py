"""HR Admin only. The router-level dependency blocks every other role."""
from fastapi import APIRouter, Depends, Query, Response, status
from typing import Annotated
from models.enums import ApplicationStatus, JobStatus
from models.enums.hr_account_status_enum import HRAccountStatus
from sqlalchemy.ext.asyncio import AsyncSession
from models.enums import HRRole
from models.db.flow_wise.schema import HRUser
from models.db.connection_database import get_db_session
from controllers.hr_admin_controller import HRAdminController
from controllers.hr_member_controller import HRReviewReader
from dependencies import require_roles
from schema.applicant_review_schema import ApplicantDetailOut, ApplicantSummaryOut
from schema.company_schema import CompanyResponse, CompanyUpdateRequest
from schema.hr_member_schema import (
    MemberCreateRequest,
    MemberOut,
    MemberUpdateRequest,
)
from schema.hr_common_schema import Page
from schema.posting_schema import PostingOut

'''

crud operations on hr  
every function that hr do the admin can do the same but with more privileges


'''

require_admin = require_roles(HRRole.ADMIN)
hr_admin_router = APIRouter(
    prefix="/api/v1/hr/admin",
    tags=["HR - Admin"],
    dependencies=[Depends(require_admin)],
)

CurrentAdmin = Annotated[HRUser, Depends(require_admin)]


# ---------------- company profile ----------------
@hr_admin_router.get("/company", response_model=CompanyResponse)
async def get_company(current: CurrentAdmin, session: AsyncSession = Depends(get_db_session)):
    return await HRAdminController(session).get_company(current)


@hr_admin_router.patch("/company", response_model=CompanyResponse)
async def update_company(data: CompanyUpdateRequest, current: CurrentAdmin, session: AsyncSession = Depends(get_db_session)):
    return await HRAdminController(session).update_company(current, data)


# ---------------- HR member accounts ----------------
@hr_admin_router.post(
    "/members",
    response_model=MemberOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create an HR Member (starts as PENDING)",
)
async def create_member(data: MemberCreateRequest, current: CurrentAdmin, session: AsyncSession = Depends(get_db_session)):
    return await HRAdminController(session).create_member(current, data)


@hr_admin_router.get("/members", response_model=Page[MemberOut])
async def list_members(
    current: CurrentAdmin,
    session: AsyncSession = Depends(get_db_session),
    status_filter: HRAccountStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await HRAdminController(session).list_members(
        current, status=status_filter, search=search, limit=limit, offset=offset
    )


@hr_admin_router.get("/members/{member_id}", response_model=MemberOut)
async def get_member(member_id: int, current: CurrentAdmin, session: AsyncSession = Depends(get_db_session)):
    return await HRAdminController(session).get_member(current, member_id)


@hr_admin_router.patch("/members/{member_id}", response_model=MemberOut)
async def update_member(
    member_id: int, data: MemberUpdateRequest, current: CurrentAdmin, session: AsyncSession = Depends(get_db_session)
):
    return await HRAdminController(session).update_member(current, member_id, data)


@hr_admin_router.post("/members/{member_id}/approve", response_model=MemberOut)
async def active_member(member_id: int, current: CurrentAdmin, session: AsyncSession = Depends(get_db_session)):
    return await HRAdminController(session).active_member(current, member_id)


@hr_admin_router.post("/members/{member_id}/disable", response_model=MemberOut)
async def disable_member(
    member_id: int,
    current: CurrentAdmin,
    session: AsyncSession = Depends(get_db_session),
):
    return await HRAdminController(session).disable_member(
        current, member_id
    )


@hr_admin_router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(member_id: int, current: CurrentAdmin, session: AsyncSession = Depends(get_db_session)):
    await HRAdminController(session).disable_member(current, member_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------- read-only oversight ----------------
@hr_admin_router.get("/postings", response_model=Page[PostingOut], summary="View postings (read-only)")
async def admin_list_postings(
    current: CurrentAdmin,
    session: AsyncSession = Depends(get_db_session),
    status_filter: JobStatus | None = Query(default=None, alias="status"),
    job_title_id: int | None = None,
    created_by: int | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await HRReviewReader(session).list_postings(
        current.company_id,
        status=status_filter,
        job_title_id=job_title_id,
        created_by=created_by,
        limit=limit,
        offset=offset,
    )


@hr_admin_router.get("/postings/{job_id}", response_model=PostingOut)
async def admin_get_posting(job_id: int, current: CurrentAdmin, session: AsyncSession = Depends(get_db_session)):
    return await HRReviewReader(session).get_posting(current.company_id, job_id)


@hr_admin_router.get("/postings/{job_id}/applicants", response_model=Page[ApplicantSummaryOut])
async def admin_list_applicants(
    job_id: int,
    current: CurrentAdmin,
    session: AsyncSession = Depends(get_db_session),
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await HRReviewReader(session).list_applicants(
        current.company_id, job_id, status=status_filter, limit=limit, offset=offset
    )


@hr_admin_router.get("/applicants/{application_id}", response_model=ApplicantDetailOut)
async def admin_get_applicant(application_id: int, current: CurrentAdmin, session: AsyncSession = Depends(get_db_session)):
    return await HRReviewReader(session).get_applicant(current.company_id, application_id)
