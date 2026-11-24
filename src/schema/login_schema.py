from pydantic import BaseModel,EmailStr
from schema import PasswordField

class Login(PasswordField):
    email: EmailStr
