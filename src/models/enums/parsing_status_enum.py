from enum import Enum

class ParsingStatus(str,Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"