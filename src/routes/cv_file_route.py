from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.cv_file_controller import CvFileController
from src.models.db.connection_database import get_db_session
from src.schema.cv_file_schema import CvFileResponse


router = APIRouter(
    prefix="/api/cv-files",
    tags=["CV Files"],
)


@router.post(
    "/upload/{candidate_id}",
    response_model=CvFileResponse,
)
async def upload_cv(
    candidate_id: int,
    file: UploadFile = File(...),
    db_session: AsyncSession = Depends(get_db_session),
):
    return await CvFileController.upload_cv(
        candidate_id=candidate_id,
        file=file,
        db_session=db_session,
    )