from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.db.flow_wise.schema import Job
from schema import JobCreateRequest, JobUpdateRequest


class JobRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, job_data: JobCreateRequest) -> Job:
        db_job = Job(**job_data.model_dump())

        try:
            self.session.add(db_job)
            await self.session.commit()
            await self.session.refresh(db_job)
            return db_job
        except Exception:
            await self.session.rollback()
            raise

    async def get_job_by_id(self, job_id: int) -> Job | None:
        query = select(Job).where(Job.id == job_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

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
            .order_by(Job.id)
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_job(
        self,
        job: Job,
        job_data: JobUpdateRequest,
    ) -> Job:
        updates = job_data.model_dump(exclude_unset=True)

        for key, value in updates.items():
            setattr(job, key, value)

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