from enum import Enum

class JobStatus(str, Enum):
    DRAFT = "drafted"
    PUBLISHED = "published"
    CLOSED = "closed"