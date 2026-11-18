from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.candidate_repository import CandidateRepository
from src.schema.candidate_schema import  CandidateCreateRequest,  CandidateUpdateStatus


class CandidateService:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.candidate_repository = CandidateRepository(db_session)

    async def create_candidate(self, candidate_data: CandidateCreateRequest):
        try:
            existing_candidate = (
                await self.candidate_repository.get_candidate_by_email(
                    candidate_data.email
                )
            )

            if existing_candidate:
                raise ValueError("Candidate with this email already exists.")

            candidate = await self.candidate_repository.create_candidate(
                candidate_data
            )

            await self.db_session.commit()
            await self.db_session.refresh(candidate)

            return candidate

        except Exception:
            await self.db_session.rollback()
            raise

    async def get_candidate_by_id(self, candidate_id: int):
        candidate = await self.candidate_repository.get_candidate_by_id(
            candidate_id
        )

        if candidate is None:
            raise ValueError("Candidate not found.")

        return candidate

    async def get_candidate_by_email(self, email: str):
        candidate = await self.candidate_repository.get_candidate_by_email(
            email
        )

        if candidate is None:
            raise ValueError("Candidate not found.")

        return candidate

    async def update_candidate_status(self, candidate_id: int, candidate_data: CandidateUpdateStatus):
        try:
            candidate = await self.get_candidate_by_id(candidate_id)

            candidate = await self.candidate_repository.update_candidate_status(
                candidate=candidate,
                candidate_data=candidate_data,
            )

            await self.db_session.commit()
            await self.db_session.refresh(candidate)

            return candidate

        except Exception:
            await self.db_session.rollback()
            raise

    async def delete_candidate(self, candidate_id: int):
        try:
            candidate = await self.get_candidate_by_id(candidate_id)

            await self.candidate_repository.delete_candidate(candidate)

            await self.db_session.commit()

            return True

        except Exception:
            await self.db_session.rollback()
            raise