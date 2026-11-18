from pydantic import BaseModel, ConfigDict, Field, field_validator
from . import ExperienceItem, EducationItem


def _normalize_items(value, key: str) -> list[dict]:
    """Coerce model output into a list of dicts for a nested section."""

    if value is None:
        return []

    if isinstance(value, dict):
        value = [value]

    if not isinstance(value, list):
        return []

    items = []
    for entry in value:
        if isinstance(entry, dict):
            items.append(entry)
        elif isinstance(entry, str) and entry.strip():
            items.append({key: entry})

    return items

class ParsedCvData(BaseModel):
    """JSON structure returned by the cv extraction model."""

    model_config = ConfigDict(extra="ignore")

    name: str = ""
    email: str = ""
    phone: str = ""
    website: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    other_details: list[str] = Field(default_factory=list)

    @field_validator("name", "email", "phone", "website", mode="before")
    @classmethod
    def normalize_text(cls, value):
        if value is None:
            return ""
        if isinstance(value, (list, dict)):
            return ""
        return str(value)

    @field_validator("skills", "other_details", mode="before")
    @classmethod
    def normalize_string_list(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, dict):
            return [str(item) for item in value.values() if item]
        if isinstance(value, list):
            return [str(item) for item in value if item is not None]
        return []

    @field_validator("experience", mode="before")
    @classmethod
    def normalize_experience(cls, value):
        return _normalize_items(value, key="title")

    @field_validator("education", mode="before")
    @classmethod
    def normalize_education(cls, value):
        return _normalize_items(value, key="degree")
