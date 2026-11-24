from pydantic import BaseModel,EmailStr
from models.enums import HRRole,HRAccountStatus

class HRUserOut(BaseModel):
    id:int
    email:EmailStr
    full_name: str
    company_id: int
    role:HRRole
    status:HRAccountStatus