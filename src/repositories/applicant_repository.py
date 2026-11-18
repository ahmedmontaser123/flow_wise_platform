"""Applicants = applications to a posting, joined to the CV file and candidate.

applications.cv_file_id -> cv_files.candidate_id -> candidates
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.db.flow_wise.schema import Application, Candidate, CvFile, HRUser, Job
from models.enums import ApplicationStatus


class ApplicantRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_for_posting(
        self,
        job_id: int,
        *,
        status: ApplicationStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[tuple[Application, Candidate]], int]:
        conditions = [Application.job_id == job_id]
        if status is not None:
            conditions.append(Application.status == status)

        total = await self.session.scalar(
            select(func.count()).select_from(Application).where(*conditions)
        )
        query = (
            select(Application, Candidate)
            .join(CvFile, Application.cv_file_id == CvFile.id)
            .join(Candidate, CvFile.candidate_id == Candidate.id)
            .where(*conditions)
            .order_by(Application.created_at.desc(), Application.id.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = (await self.session.execute(query)).all()
        return [(row[0], row[1]) for row in rows], int(total or 0)

    async def get(self, company_id: int, application_id: int) -> Application | None:
        """Application only if its posting belongs to this company."""
        query = (
            select(Application)
            .join(Job, Application.job_id == Job.id)
            .join(HRUser, Job.created_by == HRUser.id)
            .where(Application.id == application_id, HRUser.company_id == company_id)
            .options(
                selectinload(Application.job),
                selectinload(Application.cv_file).selectinload(CvFile.candidate),
                selectinload(Application.cv_file).selectinload(CvFile.parsed),
            )
        )
        return (await self.session.execute(query)).scalar_one_or_none()
