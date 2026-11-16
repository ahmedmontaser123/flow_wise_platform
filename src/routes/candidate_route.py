from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.candidate_controller import CandidateController
from src.models.db.connection_database import get_db_session

from src.schema.candidate_schema import CandidateCreateRequest, CandidateUpdateStatus, CandidateResponse



router = APIRouter(
    prefix="/api/candidates",
    tags=["Candidates"],
)


@router.post(
    "/",
    response_model=CandidateResponse,
    status_code=201,
)
async def create_candidate(candidate_data: CandidateCreateRequest, db_session: AsyncSession = Depends(get_db_session)):
    return await CandidateController.create_candidate(
        candidate_data=candidate_data,
        db_session=db_session,
    )


@router.get(
    "/{candidate_id}",
    response_model=CandidateResponse,
)
async def get_candidate_by_id(candidate_id: int, db_session: AsyncSession = Depends(get_db_session)):
    return await CandidateController.get_candidate_by_id(
        candidate_id=candidate_id,
        db_session=db_session,
    )


@router.get(
    "/email/{email}",
    response_model=CandidateResponse,
)
async def get_candidate_by_email(email: str, db_session: AsyncSession = Depends(get_db_session)):
    return await CandidateController.get_candidate_by_email(
        email=email,
        db_session=db_session,
    )


@router.patch(
    "/{candidate_id}/status",
    response_model=CandidateResponse,
)
async def update_candidate_status(candidate_id: int, candidate_data: CandidateUpdateStatus, db_session: AsyncSession = Depends(get_db_session)):
    return await CandidateController.update_candidate_status(
        candidate_id=candidate_id,
        candidate_data=candidate_data,
        db_session=db_session,
    )


@router.delete(
    "/{candidate_id}",
)
async def delete_candidate(
    candidate_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    return await CandidateController.delete_candidate(
        candidate_id=candidate_id,
        db_session=db_session,
    )