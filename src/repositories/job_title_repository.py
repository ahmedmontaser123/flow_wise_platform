from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.db.flow_wise.schema import Job
from models.db.flow_wise.schema.job_title import JobTitle

from helpers.hr_utils import like_pattern


class JobTitleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, company_id: int, title_id: int) -> JobTitle | None:
        query = select(JobTitle).where(
            JobTitle.id == title_id, JobTitle.company_id == company_id
        )
        return (await self.session.execute(query)).scalar_one_or_none()

    async def name_taken(
        self, company_id: int, name: str, exclude_id: int | None = None
    ) -> bool:
        query = select(JobTitle.id).where(
            JobTitle.company_id == company_id,
            func.lower(JobTitle.name) == name.lower(),
        )
        if exclude_id is not None:
            query = query.where(JobTitle.id != exclude_id)
        return (await self.session.execute(query.limit(1))).first() is not None

    async def list(
        self,
        company_id: int,
        *,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[JobTitle], int]:
        conditions = [JobTitle.company_id == company_id]
        if search:
            pattern = like_pattern(search.strip())
            conditions.append(
                or_(JobTitle.name.ilike(pattern), JobTitle.department.ilike(pattern))
            )
        total = await self.session.scalar(
            select(func.count()).select_from(JobTitle).where(*conditions)
        )
        result = await self.session.execute(
            select(JobTitle)
            .where(*conditions)
            .order_by(func.lower(JobTitle.name))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all()), int(total or 0)

    async def count_postings(self, title_id: int) -> int:
        total = await self.session.scalar(
            select(func.count()).select_from(Job).where(Job.job_title_id == title_id)
        )
        return int(total or 0)

    async def add(self, title: JobTitle) -> JobTitle:
        self.session.add(title)
        await self.session.flush()
        return title

    async def delete(self, title: JobTitle) -> None:
        await self.session.delete(title)
        await self.session.flush()
