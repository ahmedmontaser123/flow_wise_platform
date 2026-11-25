from datetime import datetime
from pydantic import BaseModel, ConfigDict
from models.enums import ApplicationStatus

class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cv_file_id: int
    job_id: int
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime