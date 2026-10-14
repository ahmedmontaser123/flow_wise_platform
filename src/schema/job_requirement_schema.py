from models.enums import RequirementType

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from models.enums import RequirementType


class JobRequirementCreateRequest(BaseModel):
    job_id: int = Field(..., gt=0)
    type: RequirementType
    content: str = Field(..., min_length=1)
    required: bool = True
    weight: float = Field(default=1.0, gt=0)


class JobRequirementUpdateRequest(BaseModel):
    type: RequirementType | None = None
    content: str | None = Field(None, min_length=1)
    required: bool | None = None
    weight: float | None = Field(None, gt=0)

    @model_validator(mode="after")
    def validate_non_nullable_fields(self):
        non_nullable_fields = (
            "type",
            "content",
            "required",
            "weight",
        )

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
    type: RequirementType
    content: str
    required: bool
    weight: float