from typing import Annotated


from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from models.db.connection_database import get_db_session 
from schema.job_schema import (
    JobCreateRequest, 
    JobResponse, 
    JobUpdateRequest,
    JobWithApplicationsResponse
)
from controllers.job_controller import JobController
from dependencies import get_current_hr
from models.db.flow_wise.schema import HRUser


CurrentHRUser = Annotated[
    HRUser,
    Depends(get_current_hr)
]

router = APIRouter(
    prefix="/api/jobs"
)


    
@router.get(
    "/public", 
    response_model=List[JobResponse], 
    status_code=status.HTTP_200_OK,
    tags=["Jobs (Public)"], 
    summary="Get all published jobs (For Candidates)",
    description="Retrieves a list of all published jobs. No HR authentication required."
)
async def get_public_jobs_endpoint(
    limit: int = 100,
    offset: int = 0,
    db_session: AsyncSession = Depends(get_db_session)
):
    return await JobController.get_active_jobs(db_session=db_session, limit=limit, offset=offset)