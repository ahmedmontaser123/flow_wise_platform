from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CvFileCreateRequest(BaseModel):
    candidate_id: int = Field(..., gt=0)
    file_path: str = Field(..., min_length=1,max_length=500)


class CvFileResponse(BaseModel):
    id: int
    candidate_id: int
    file_path: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)