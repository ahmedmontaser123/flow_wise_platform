from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.db.flow_wise.schema import HRUser, Job
from models.db.flow_wise.schema.job_title import JobTitle
from models.enums import ApplicationStatus, JobStatus

from helpers.hr_errors import conflict, not_found
from repositories.applicant_repository import ApplicantRepository
from repositories.job_title_repository import JobTitleRepository
from repositories.posting_repository import PostingRepository
from helpers.hr_utils import utcnow, utcnow_naive
from schema.applicant_review_schema import ApplicantDetailOut, ApplicantSummaryOut, ApplicationStatusUpdateRequest
from schema.job_title_schema import JobTitleCreateRequest, JobTitleOut, JobTitleUpdateRequest
from schema.hr_common_schema import Page
from schema.posting_schema import PostingCreateRequest, PostingOut, PostingUpdateRequest
from schema.applicant_review_schema import CandidateBrief

# Hiring pipeline, in order. An applicant can move forward (skipping steps is
# allowed) or be rejected at any step. HIRED and REJECTED are final.
PIPELINE: list[ApplicationStatus] = [
    ApplicationStatus.NOT_RECEIVED,
    ApplicationStatus.RECEIVED,
    ApplicationStatus.SCREENED,
    ApplicationStatus.SHORTLISTED,
    ApplicationStatus.INTERVIEW,
    ApplicationStatus.OFFER,
    ApplicationStatus.HIRED,
]
FINAL_STATUSES = {ApplicationStatus.HIRED, ApplicationStatus.REJECTED}


def allowed_next_statuses(current: ApplicationStatus) -> list[ApplicationStatus]:
    if current in FINAL_STATUSES:
        return []
    later = PIPELINE[PIPELINE.index(current) + 1 :]
    return later + [ApplicationStatus.REJECTED]


def _posting_out(job: Job, applicants_count: int) -> PostingOut:
    return PostingOut.model_validate(job).model_copy(
        update={"applicants_count": applicants_count}
    )


class HRReviewReader:
    """Read-only views of postings and applicants.

    Used by HR Members, and by the HR Admin for oversight (Admin can look, not act).
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.postings = PostingRepository(session)
        self.applicants = ApplicantRepository(session)

    async def list_postings(self, company_id: int, **filters) -> Page[PostingOut]:
        limit, offset = filters.pop("limit"), filters.pop("offset")
        rows, total = await self.postings.list(
            company_id, limit=limit, offset=offset, **filters
        )
        return Page[PostingOut](
            items=[_posting_out(job, n) for job, n in rows],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_posting_or_404(self, company_id: int, job_id: int) -> Job:
        job = await self.postings.get(company_id, job_id)
        if job is None:
            raise not_found("Posting")
        return job

    async def get_posting(self, company_id: int, job_id: int) -> PostingOut:
        job = await self.get_posting_or_404(company_id, job_id)
        return _posting_out(job, await self.postings.count_applicants(job.id))

    async def list_applicants(
        self,
        company_id: int,
        job_id: int,
        *,
        status: ApplicationStatus | None,
        limit: int,
        offset: int,
    ) -> Page[ApplicantSummaryOut]:
        await self.get_posting_or_404(company_id, job_id)
        rows, total = await self.applicants.list_for_posting(
            job_id, status=status, limit=limit, offset=offset
        )
        items = [
            ApplicantSummaryOut(
                application_id=app.id,
                job_id=app.job_id,
                status=app.status,
                applied_at=app.created_at,
                updated_at=app.updated_at,
                cv_file_id=app.cv_file_id,
                candidate=CandidateBrief.model_validate(candidate),
            )
            for app, candidate in rows
        ]
        return Page[ApplicantSummaryOut](items=items, total=total, limit=limit, offset=offset)

    async def get_applicant(self, company_id: int, application_id: int) -> ApplicantDetailOut:
        app = await self.applicants.get(company_id, application_id)
        if app is None:
            raise not_found("Applicant")
        parsed = app.cv_file.parsed
        return ApplicantDetailOut(
            application_id=app.id,
            job_id=app.job_id,
            job_title=app.job.title,
            status=app.status,
            applied_at=app.created_at,
            updated_at=app.updated_at,
            cv_file_id=app.cv_file_id,
            cv_file_path=app.cv_file.file_path,
            cv_parsing_status=parsed.status if parsed else None,
            cv_parsed_data=parsed.parsed_data if parsed else None,
            candidate=CandidateBrief.model_validate(app.cv_file.candidate),
            allowed_next_statuses=allowed_next_statuses(app.status),
        )


class HRMemberController(HRReviewReader):
    """Operational actions: job titles, postings and applicant review."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.titles = JobTitleRepository(session)

    # ---------------- job titles ----------------
    async def _title_or_404(self, company_id: int, title_id: int) -> JobTitle:
        title = await self.titles.get(company_id, title_id)
        if title is None:
            raise not_found("Job title")
        return title

    async def create_job_title(self, user: HRUser, data: JobTitleCreateRequest) -> JobTitleOut:
        if await self.titles.name_taken(user.company_id, data.name):
            raise conflict("A job title with this name already exists")
        try:
            title = await self.titles.add(
                JobTitle(
                    company_id=user.company_id,
                    name=data.name,
                    department=data.department,
                    description=data.description,
                    created_by=user.id,
                )
            )
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise conflict("A job title with this name already exists")
        await self.session.refresh(title)
        return JobTitleOut.model_validate(title)

    async def list_job_titles(
        self, user: HRUser, *, search: str | None, limit: int, offset: int
    ) -> Page[JobTitleOut]:
        items, total = await self.titles.list(
            user.company_id, search=search, limit=limit, offset=offset
        )
        return Page[JobTitleOut](
            items=[JobTitleOut.model_validate(t) for t in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_job_title(self, user: HRUser, title_id: int) -> JobTitleOut:
        return JobTitleOut.model_validate(await self._title_or_404(user.company_id, title_id))

    async def update_job_title(
        self, user: HRUser, title_id: int, data: JobTitleUpdateRequest
    ) -> JobTitleOut:
        title = await self._title_or_404(user.company_id, title_id)
        updates = data.model_dump(exclude_unset=True)
        if "name" in updates:
            if updates["name"] is None:
                raise conflict("Name cannot be empty")
            if await self.titles.name_taken(user.company_id, updates["name"], exclude_id=title.id):
                raise conflict("A job title with this name already exists")
        for key, value in updates.items():
            setattr(title, key, value)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise conflict("A job title with this name already exists")
        await self.session.refresh(title)
        return JobTitleOut.model_validate(title)

    async def delete_job_title(self, user: HRUser, title_id: int) -> None:
        title = await self._title_or_404(user.company_id, title_id)
        if await self.titles.count_postings(title.id) > 0:
            raise conflict("This job title is used by postings and cannot be deleted")
        await self.titles.delete(title)
        await self.session.commit()

    # ---------------- postings ----------------
    async def create_posting(self, user: HRUser, data: PostingCreateRequest) -> PostingOut:
        title = await self._title_or_404(user.company_id, data.job_title_id)
        now = utcnow_naive()
        job = await self.postings.add(
            Job(
                job_title_id=title.id,
                title=data.title or title.name,
                description=data.description,
                location=data.location,
                employment_type=data.employment_type,
                experience_level=data.experience_level,
                status=JobStatus.DRAFT,
                created_by=user.id,
                created_at=now,
                updated_at=now,
            )
        )
        await self.session.commit()
        return _posting_out(job, 0)

    async def update_posting(
        self, user: HRUser, job_id: int, data: PostingUpdateRequest
    ) -> PostingOut:
        job = await self.get_posting_or_404(user.company_id, job_id)
        if job.status == JobStatus.CLOSED:
            raise conflict("A closed posting cannot be edited. Open it again first")

        updates = data.model_dump(exclude_unset=True)
        for required in ("job_title_id", "title", "description", "employment_type"):
            if required in updates and updates[required] is None:
                raise conflict(f"{required} cannot be empty")
        if "job_title_id" in updates:
            await self._title_or_404(user.company_id, updates["job_title_id"])

        for key, value in updates.items():
            setattr(job, key, value)
        job.updated_at = utcnow_naive()
        await self.session.commit()
        return _posting_out(job, await self.postings.count_applicants(job.id))

    async def open_posting(self, user: HRUser, job_id: int) -> PostingOut:
        job = await self.get_posting_or_404(user.company_id, job_id)
        if job.status == JobStatus.PUBLISHED:
            raise conflict("Posting is already open")
        job.status = JobStatus.PUBLISHED
        job.updated_at = utcnow_naive()
        await self.session.commit()
        return _posting_out(job, await self.postings.count_applicants(job.id))

    async def close_posting(self, user: HRUser, job_id: int) -> PostingOut:
        job = await self.get_posting_or_404(user.company_id, job_id)
        if job.status != JobStatus.PUBLISHED:
            raise conflict("Only an open (published) posting can be closed")
        job.status = JobStatus.CLOSED
        job.updated_at = utcnow_naive()
        await self.session.commit()
        return _posting_out(job, await self.postings.count_applicants(job.id))

    # ---------------- applicant review ----------------
    async def update_applicant_status(
        self, user: HRUser, application_id: int, data: ApplicationStatusUpdateRequest
    ) -> ApplicantDetailOut:
        app = await self.applicants.get(user.company_id, application_id)
        if app is None:
            raise not_found("Applicant")

        allowed = allowed_next_statuses(app.status)
        if data.status not in allowed:
            names = ", ".join(s.value for s in allowed) or "none (final status)"
            raise conflict(
                f"Cannot move applicant from '{app.status.value}' to "
                f"'{data.status.value}'. Allowed: {names}"
            )
        app.status = data.status
        app.updated_at = utcnow()
        await self.session.commit()
        return await self.get_applicant(user.company_id, application_id)
