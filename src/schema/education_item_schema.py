from pydantic import BaseModel, ConfigDict, Field, field_validator

class EducationItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    degree: str = ""
    institution: str = ""
    year: str = ""

    @field_validator("degree", "institution", "year", mode="before")
    @classmethod
    def normalize_text(cls, value):
        return "" if value is None else str(value)
