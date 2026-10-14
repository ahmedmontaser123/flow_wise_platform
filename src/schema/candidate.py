from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict

from models.enums import CandidateStatus


class CandidateCreateRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None
    education: str | None = None
    portfolio: str | None = None
    status: CandidateStatus = CandidateStatus.APPLIED


class CandidateUpdateRequest(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    education: str | None = None
    portfolio: str | None = None
    status: CandidateStatus | None = None


class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: str | None
    created_at: datetime
    education: str | None
    portfolio: str | None
    status: CandidateStatus