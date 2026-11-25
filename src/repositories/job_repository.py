from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload  
from datetime import datetime, timezone

from models.db.flow_wise.schema import Job, JobRequirement
from schema import JobCreateRequest, JobUpdateRequest

class JobRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, job_data: JobCreateRequest) -> Job:
        job_dict = job_data.model_dump(exclude={"schema_definition", "weight"})
        
        db_job = Job(**job_dict)

        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        db_job.created_at = now_naive
        db_job.updated_at = now_naive

        try:
            self.session.add(db_job)
            await self.session.flush() 
            db_requirement = JobRequirement(
                job_id=db_job.id,
                schema_definition=job_data.schema_definition,
                weight=job_data.weight
            )
            self.session.add(db_requirement)

            await self.session.commit()
            await self.session.refresh(db_job)

            setattr(db_job, "schema_definition", db_requirement.schema_definition)
            setattr(db_job, "weight", db_requirement.weight)

            return db_job

        except Exception:
            await self.session.rollback()
            raise

    async def get_job_by_id(self, job_id: int) -> Job | None:
        query = select(Job).options(selectinload(Job.requirements)).where(Job.id == job_id)
        result = await self.session.execute(query)
        job = result.scalar_one_or_none()
        
        if job and job.requirements:
            setattr(job, "schema_definition", job.requirements[0].schema_definition)
            setattr(job, "weight", job.requirements[0].weight)
            
        return job

    async def get_all_jobs(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Job]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")

        if offset < 0:
            raise ValueError("offset cannot be negative")

        query = (
            select(Job)
            .options(selectinload(Job.requirements)) 
            .order_by(Job.id)
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        jobs = list(result.scalars().all())
        
        for job in jobs:
            if job.requirements:
                setattr(job, "schema_definition", job.requirements[0].schema_definition)
                setattr(job, "weight", job.requirements[0].weight)
                
        return jobs

    async def get_active_jobs(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Job]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")

        if offset < 0:
            raise ValueError("offset cannot be negative")

        query = (
            select(Job)
            .options(selectinload(Job.requirements)) 
            .where(Job.status == "published")
            .order_by(Job.id)
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        jobs = list(result.scalars().all())
        
        for job in jobs:
            if job.requirements:
                setattr(job, "schema_definition", job.requirements[0].schema_definition)
                setattr(job, "weight", job.requirements[0].weight)
                
        return jobs

    async def update_job(
        self,
        job: Job,
        job_data: JobUpdateRequest,
    ) -> Job:
        updates = job_data.model_dump(exclude_unset=True)

        for key, value in updates.items():
            setattr(job, key, value)

        job.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        try:
            await self.session.commit()
            await self.session.refresh(job)
            return job
        except Exception:
            await self.session.rollback()
            raise

    async def delete_job(self, job: Job) -> bool:
        try:
            await self.session.delete(job)
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            raise


    async def get_job_with_applications(self, job_id: int) -> Job | None:
        query = (
            select(Job)
            .options(
                selectinload(Job.requirements),
                selectinload(Job.applications) 
            )
            .where(Job.id == job_id)
        )
        result = await self.session.execute(query)
        job = result.scalar_one_or_none()
        
        
        if job and job.requirements:
            setattr(job, "schema_definition", job.requirements[0].schema_definition)
            setattr(job, "weight", job.requirements[0].weight)
            
        return job    