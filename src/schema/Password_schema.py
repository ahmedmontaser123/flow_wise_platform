from pydantic import BaseModel, Field, field_validator

class PasswordField(BaseModel):
    """Mixin-style base: any model with a `password` field gets the rules."""

    password: str = Field(..., min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def check_password(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes")
        if value.strip() != value:
            raise ValueError("Password must not start or end with spaces")
        if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one letter and one number")
        return value
    


class ChangePasswordRequest(BaseModel):
    current_password:PasswordField
    new_password:PasswordField








