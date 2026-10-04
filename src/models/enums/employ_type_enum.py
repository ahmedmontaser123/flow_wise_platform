from enum import Enum

class EmployType(str, Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    INTERN = "Intern"
    FREELANCE = "Freelance"