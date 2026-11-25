from enum import Enum


class RequirementType(str, Enum):
    SKILL = "SKILL"
    EXPERIENCE = "EXPERIENCE"
    EDUCATION = "EDUCATION"
    LANGUAGE = "LANGUAGE"