from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.db.flow_wise.schema import Application, Candidate, CvFile


class DashboardRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_candidate_dashboard(
        self, candidate_id: int, job_id: int | None = None
    ) -> tuple[Candidate | None, list[Application]]:
        candidate_result = await self.session.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = candidate_result.scalar_one_or_none()
        if candidate is None:
            return None, []

        query = (
            select(Application)
            .join(Application.cv_file)
            .where(CvFile.candidate_id == candidate_id)
            .options(
                joinedload(Application.job),
                joinedload(Application.cv_file).joinedload(CvFile.parsed),
            )
            .order_by(Application.created_at.desc())
        )
        if job_id is not None:
            query = query.where(Application.job_id == job_id)

        result = await self.session.execute(query)
        return candidate, list(result.unique().scalars().all())
