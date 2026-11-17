import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.candidate_service import CandidateService
from src.schema.candidate_schema import (
    CandidateCreateRequest,
    CandidateUpdateStatus,
    CandidateResponse,
)


logger = logging.getLogger(__name__)


class CandidateController:

    @staticmethod
    async def create_candidate(candidate_data: CandidateCreateRequest, db_session: AsyncSession) -> CandidateResponse:
        try:
            service = CandidateService(db_session)

            candidate = await service.create_candidate(
                candidate_data=candidate_data,
            )

            return CandidateResponse.model_validate(candidate)

        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc

        except Exception as exc:
            logger.exception("Candidate creation failed")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while creating the candidate.",
            ) from exc

    @staticmethod
    async def get_candidate_by_id(candidate_id: int, db_session: AsyncSession) -> CandidateResponse:
        try:
            service = CandidateService(db_session)

            candidate = await service.get_candidate_by_id(
                candidate_id=candidate_id,
            )

            return CandidateResponse.model_validate(candidate)

        except ValueError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            ) from exc

        except Exception as exc:
            logger.exception("Candidate retrieval failed")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while retrieving the candidate.",
            ) from exc

    @staticmethod
    async def get_candidate_by_email(email: str, db_session: AsyncSession) -> CandidateResponse:
        try:
            service = CandidateService(db_session)

            candidate = await service.get_candidate_by_email(
                email=email,
            )

            return CandidateResponse.model_validate(candidate)

        except ValueError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            ) from exc

        except Exception as exc:
            logger.exception("Candidate retrieval by email failed")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while retrieving the candidate.",
            ) from exc

    @staticmethod
    async def update_candidate_status(candidate_id: int, candidate_data: CandidateUpdateStatus, db_session: AsyncSession) -> CandidateResponse:
        try:
            service = CandidateService(db_session)

            candidate = await service.update_candidate_status(
                candidate_id=candidate_id,
                candidate_data=candidate_data,
            )

            return CandidateResponse.model_validate(candidate)

        except ValueError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            ) from exc

        except Exception as exc:
            logger.exception("Candidate status update failed")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while updating the candidate.",
            ) from exc

    @staticmethod
    async def delete_candidate(candidate_id: int, db_session: AsyncSession):
        try:
            service = CandidateService(db_session)

            await service.delete_candidate(
                candidate_id=candidate_id,
            )

            return {
                "message": "Candidate deleted successfully."
            }

        except ValueError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            ) from exc

        except Exception as exc:
            logger.exception("Candidate deletion failed")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while deleting the candidate.",
            ) from exc