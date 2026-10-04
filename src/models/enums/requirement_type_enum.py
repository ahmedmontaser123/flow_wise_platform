from enum import Enum
class RequirementType(str, Enum):
    SKILL = "Skill"
    EXPERIENCE = "Experience"
    EDUCATION = "Education"
    LANGUAGE = "Language"