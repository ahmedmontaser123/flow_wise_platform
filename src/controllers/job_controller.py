from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# تمت إضافة JobUpdateRequest هنا للاستيراد
from src.schema.job_schema import JobCreateRequest, JobResponse, JobUpdateRequest
from src.repositories.job_repository import JobRepository

from src.schema.job_schema import JobWithApplicationsResponse

class JobController:
    
    @staticmethod
    async def create_job(
        job_data: JobCreateRequest,
        hr_id: int, 
        db_session: AsyncSession
    ) -> JobResponse:
        """
        Creates a new job after injecting the authenticated HR's ID.
        """
        try:
            job_repo = JobRepository(db_session)
            job_data.created_by = hr_id
            created_job = await job_repo.create_job(job_data)
            return JobResponse.model_validate(created_job)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while creating the job: {str(e)}"
            )

    @staticmethod
    async def get_all_jobs(
        db_session: AsyncSession,
        limit: int = 100,
        offset: int = 0
    ) -> List[JobResponse]:
        """
        Retrieves a list of all jobs with pagination (For HR).
        """
        try:
            job_repo = JobRepository(db_session)
            jobs = await job_repo.get_all_jobs(limit=limit, offset=offset)
            return [JobResponse.model_validate(job) for job in jobs]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while fetching jobs: {str(e)}"
            )

    # === الدالة التي كانت مفقودة (للمسار العام) ===
    @staticmethod
    async def get_active_jobs(
        db_session: AsyncSession,
        limit: int = 100,
        offset: int = 0
    ) -> List[JobResponse]:
        """
        Retrieves a list of all active jobs for the public facing endpoint.
        """
        try:
            job_repo = JobRepository(db_session)
            active_jobs = await job_repo.get_active_jobs(limit=limit, offset=offset)
            return [JobResponse.model_validate(job) for job in active_jobs]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while fetching active jobs: {str(e)}"
            )

    # === الدالة الجديدة: تحديث حالة الوظيفة ===
    @staticmethod
    async def update_job_status(
        job_id: int,
        status_update: JobUpdateRequest,
        db_session: AsyncSession
    ) -> JobResponse:
        """
        Updates the status of an existing job (e.g., drafted -> active).
        """
        try:
            job_repo = JobRepository(db_session)
            
            # التأكد من وجود الوظيفة أولاً
            job = await job_repo.get_job_by_id(job_id)
            if not job:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Job with ID {job_id} not found."
                )
            
            # تحديث الحالة عبر المستودع
            updated_job = await job_repo.update_job(job, status_update)
            
            # إعادة حقن المتطلبات بعد التحديث (لأن session.refresh قد يمسحها من الذاكرة المؤقتة)
            if updated_job.requirements:
                setattr(updated_job, "schema_definition", updated_job.requirements[0].schema_definition)
                setattr(updated_job, "weight", updated_job.requirements[0].weight)
                
            return JobResponse.model_validate(updated_job)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while updating the job status: {str(e)}"
            )


    @staticmethod
    async def get_job_with_applications(
        job_id: int,
        db_session: AsyncSession
    ) -> JobWithApplicationsResponse:
        try:
            job_repo = JobRepository(db_session)
            job = await job_repo.get_job_with_applications(job_id)
            
            if not job:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Job with ID {job_id} not found."
                )
                
            return JobWithApplicationsResponse.model_validate(job)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while fetching the job and applications: {str(e)}"
            )    