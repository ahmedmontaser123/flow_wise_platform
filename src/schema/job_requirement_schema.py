from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

class JobRequirementCreateRequest(BaseModel):
    job_id: int = Field(..., gt=0)
    schema_definition: dict[str, Any] = Field(...) 
    weight: float = Field(default=1.0, gt=0)

class JobRequirementUpdateRequest(BaseModel):
    schema_definition: dict[str, Any] | None = None
    weight: float | None = Field(None, gt=0)

    @model_validator(mode="after")
    def validate_non_nullable_fields(self):
        non_nullable_fields = ("schema_definition", "weight")
        for field_name in non_nullable_fields:
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(f"{field_name} cannot be null.")
        return self

class JobRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    schema_definition: dict[str, Any]
    weight: float
    last_edited: datetime