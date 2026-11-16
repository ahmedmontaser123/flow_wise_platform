import logging

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.cv_file_service import CvFileService
from src.schema.cv_file_schema import CvFileResponse


logger = logging.getLogger(__name__)


class CvFileController:

    @staticmethod
    async def upload_cv(candidate_id: int, file: UploadFile, db_session: AsyncSession) -> CvFileResponse:
        try:
            service = CvFileService(db_session)

            cv_file = await service.upload_cv(
                candidate_id=candidate_id,
                file=file,
            )

            return CvFileResponse.model_validate(cv_file)

        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc

        except Exception as exc:
            logger.exception("CV upload failed")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while uploading the CV.",
            ) from exc