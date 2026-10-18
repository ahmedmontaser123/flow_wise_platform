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


'''

task create endpoint post job requirment   data 

# logic 
validation data pydantic 
get_job_email_user(id) --- > job found  create job requirment in data base '
not found  response 404  "message": "not found"

'''