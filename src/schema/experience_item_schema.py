from pydantic import BaseModel, ConfigDict, Field, field_validator

class ExperienceItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = ""
    company: str = ""
    duration: str = ""

    @field_validator("title", "company", "duration", mode="before")
    @classmethod
    def normalize_text(cls, value):
        return "" if value is None else str(value)
