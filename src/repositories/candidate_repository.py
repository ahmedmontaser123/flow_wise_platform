from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.db.flow_wise.schema import Candidate
from schema import CandidateCreateRequest, CandidateUpdateRequest


class CandidateRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_candidate(        
        self,
        candidate_data: CandidateCreateRequest,
    ) -> Candidate:
                 
        candidate = Candidate(
            full_name=candidate_data.full_name,
            email=candidate_data.email,
            phone=candidate_data.phone,
            education=candidate_data.education,
            portfolio=candidate_data.portfolio,
        )

        self.session.add(candidate)
        await self.session.commit()
        await self.session.refresh(candidate)

        return candidate

    async def get_candidate_by_id(
        self,
        candidate_id: int,
    ) -> Candidate | None:

        query = select(Candidate).where( Candidate.id == candidate_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_candidate_by_email(
        self,
        email: str,
    ) -> Candidate | None:

        query = select(Candidate).where(Candidate.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_candidate_status(
        self,
        candidate: Candidate,
        candidate_data: CandidateUpdateRequest,
    ) -> Candidate:
        
        candidate.status = candidate_data.status
        await self.session.commit()
        await self.session.refresh(candidate)
        return candidate


    async def delete_candidate(
        self,
        candidate: Candidate,
    ) -> bool:

        await self.session.delete(candidate)
        await self.session.commit()
        return True