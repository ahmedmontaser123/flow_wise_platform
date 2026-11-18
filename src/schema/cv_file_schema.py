from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CvFileCreateRequest(BaseModel):
    candidate_id: int = Field(..., gt=0)
    file_path: str = Field(..., min_length=1, max_length=500)
    file_hash: str = Field(..., min_length=64, max_length=64, description="SHA-256 hash of the CV file to prevent duplicates")


class CvFileResponse(BaseModel):
    id: int
    candidate_id: int
    file_path: str
    file_hash: Optional[str] = None  # جعلناها اختيارية تحسباً لأي بيانات قديمة
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)