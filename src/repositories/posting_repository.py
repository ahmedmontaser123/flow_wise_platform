"""Postings = rows of the existing `jobs` table.

A job belongs to a company through the HR user who created it
(jobs.created_by -> hr_users.company_id), so every query joins hr_users
and filters by company_id.
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.db.flow_wise.schema import Application, HRUser, Job
from models.enums import JobStatus


class PostingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _scoped(company_id: int):
        return (
            select(Job)
            .join(HRUser, Job.created_by == HRUser.id)
            .where(HRUser.company_id == company_id)
        )

    async def get(self, company_id: int, job_id: int) -> Job | None:
        query = self._scoped(company_id).where(Job.id == job_id)
        return (await self.session.execute(query)).scalar_one_or_none()

    async def count_applicants(self, job_id: int) -> int:
        total = await self.session.scalar(
            select(func.count()).select_from(Application).where(Application.job_id == job_id)
        )
        return int(total or 0)

    async def list(
        self,
        company_id: int,
        *,
        status: JobStatus | None = None,
        job_title_id: int | None = None,
        created_by: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[tuple[Job, int]], int]:
        """Returns ([(job, applicants_count), ...], total)."""
        conditions = [HRUser.company_id == company_id]
        if status is not None:
            conditions.append(Job.status == status)
        if job_title_id is not None:
            conditions.append(Job.job_title_id == job_title_id)
        if created_by is not None:
            conditions.append(Job.created_by == created_by)

        total = await self.session.scalar(
            select(func.count())
            .select_from(Job)
            .join(HRUser, Job.created_by == HRUser.id)
            .where(*conditions)
        )

        applicants = (
            select(Application.job_id, func.count(Application.id).label("n"))
            .group_by(Application.job_id)
            .subquery()
        )
        query = (
            select(Job, func.coalesce(applicants.c.n, 0))
            .join(HRUser, Job.created_by == HRUser.id)
            .outerjoin(applicants, applicants.c.job_id == Job.id)
            .where(*conditions)
            .order_by(Job.created_at.desc(), Job.id.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self.session.execute(query)).all()
        return [(row[0], int(row[1])) for row in rows], int(total or 0)

    async def add(self, job: Job) -> Job:
        self.session.add(job)
        await self.session.flush()
        return job
