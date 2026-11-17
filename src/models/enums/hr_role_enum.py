from enum import Enum


class HRRole(str, Enum):
    """Role of an HR account. Exactly one ADMIN per company."""

    ADMIN = "admin"
    MEMBER = "member"
