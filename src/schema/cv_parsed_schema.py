from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from models.enums import ParsingStatus


class CvParsedCreateRequest(BaseModel):
    cv_file_id: int = Field(..., gt=0)


class CvParsedUpdateRequest(BaseModel):
    status: ParsingStatus | None = None
    parsed_data: dict[str, Any] | None = None


class CvParsedResponse(BaseModel):
    id: int
    cv_file_id: int
    parsed_data: dict[str, Any] | None = None
    status: ParsingStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)