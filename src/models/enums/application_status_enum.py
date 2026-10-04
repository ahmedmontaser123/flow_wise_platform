from enum import Enum


class ApplicationStatus(str, Enum):
    NOT_RECEIVED = "not_received"
    RECEIVED = "received"
    SCREENED = "screened"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"