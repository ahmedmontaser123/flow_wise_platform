from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.models.db.connection_database import get_db_session
from src.schema.job_schema import (
    JobCreateRequest,
    JobResponse,
    JobUpdateRequest,
    JobWithApplicationsResponse
)
from src.controllers.job_controller import JobController

# استيراد نظام المصادقة الحقيقي (CurrentHRUser)
from src.helpers.rbac import CurrentHRUser

# أزلنا الـ tags من هنا لمنع التوريث الإجباري
router = APIRouter(
    prefix="/api/jobs"
)

# تم حذف الدالة المزيفة (get_current_hr_id) بالكامل

@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Jobs (HR)"],
    summary="Create a new job",
    description="Creates a new job post. Requires HR authentication."
)
async def create_job_endpoint(
    job_data: JobCreateRequest,
    current_hr: CurrentHRUser, # استخدام المصادقة الحقيقية
    db_session: AsyncSession = Depends(get_db_session)
):
    # تمرير current_hr.id (الرقم الحقيقي) بدلاً من hr_id المزيف
    return await JobController.create_job(job_data=job_data, hr_id=current_hr.id, db_session=db_session)


@router.get(
    "",
    response_model=List[JobResponse],
    status_code=status.HTTP_200_OK,
    tags=["Jobs (HR)"],
    summary="Get all jobs",
    description="Retrieves a list of all jobs."
)
async def get_all_jobs_endpoint(
    current_hr: CurrentHRUser, # حماية المسار
    limit: int = 100,
    offset: int = 0,
    db_session: AsyncSession = Depends(get_db_session)
):
    # إذا كان get_all_jobs يحتاج إلى hr_id في الـ Controller، مرر current_hr.id هنا
    # حالياً افترضت أنه يعيد جميع الوظائف بناءً على الـ Session فقط كما كان كودك
    return await JobController.get_all_jobs(db_session=db_session, limit=limit, offset=offset)


@router.patch(
    "/{job_id}/status",
    response_model=JobResponse,
    status_code=status.HTTP_200_OK,
    tags=["Jobs (HR)"],
    summary="Update job status",
    description="Updates the status of a specific job (e.g., from drafted to published)."
)
async def update_job_status_endpoint(
    job_id: int,
    status_update: JobUpdateRequest,
    current_hr: CurrentHRUser, # حماية المسار
    db_session: AsyncSession = Depends(get_db_session)
):
    return await JobController.update_job_status(job_id=job_id, status_update=status_update, db_session=db_session)


@router.get(
    "/{job_id}/with-applications",
    response_model=JobWithApplicationsResponse,
    status_code=status.HTTP_200_OK,
    tags=["Jobs (HR)"],
    summary="Get job with all applications",
    description="Retrieves a specific job along with its submitted applications."
)
async def get_job_with_applications_endpoint(
    job_id: int,
    current_hr: CurrentHRUser, # حماية المسار
    db_session: AsyncSession = Depends(get_db_session)
):
    return await JobController.get_job_with_applications(job_id=job_id, db_session=db_session)


# === المسار العام للمرشحين يبقى بـ Tag منفصل تماماً وبدون مصادقة HR ===
@router.get(
    "/public",
    response_model=List[JobResponse],
    status_code=status.HTTP_200_OK,
    tags=["Jobs (Public)"],
    summary="Get all published jobs (For Candidates)",
    description="Retrieves a list of all published jobs. No HR authentication required."
)
async def get_public_jobs_endpoint(
    limit: int = 100,
    offset: int = 0,
    db_session: AsyncSession = Depends(get_db_session)
):
    return await JobController.get_active_jobs(db_session=db_session, limit=limit, offset=offset)