from typing import Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


class MessageOut(BaseModel):
    message: str


def _password_rules(value: str) -> str:
    # bcrypt only uses the first 72 bytes, so longer passwords are refused.
    if len(value.encode("utf-8")) > 72:
        raise ValueError("Password must be at most 72 bytes")
    if value.strip() != value:
        raise ValueError("Password must not start or end with spaces")
    if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
        raise ValueError("Password must contain at least one letter and one number")
    return value


class PasswordField(BaseModel):
    """Mixin-style base: any model with a `password` field gets the rules."""

    password: str = Field(..., min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def check_password(cls, value: str) -> str:
        return _password_rules(value)


def clean_name(value: str | None) -> str | None:
    if value is None:
        return None
    value = " ".join(value.split())
    if not value:
        raise ValueError("Must not be empty")
    return value
