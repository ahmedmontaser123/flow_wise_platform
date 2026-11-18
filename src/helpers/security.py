"""Password hashing (passlib + bcrypt) and JWT helpers."""
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from helpers.hr_auth_settings import get_hr_auth_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Used when the e-mail does not exist, so a wrong e-mail takes about as long
# as a wrong password (makes it harder to guess which e-mails are registered).
_DUMMY_HASH = pwd_context.hash("flowwise-dummy-password")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    if not hashed_password:
        pwd_context.verify(plain_password, _DUMMY_HASH)
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (UnknownHashError, ValueError):
        # Old rows that still hold a plain-text password are treated as invalid.
        return False


def burn_dummy_verify(plain_password: str) -> None:
    pwd_context.verify(plain_password, _DUMMY_HASH)


def create_access_token(
    *,
    user_id: int,
    role: str,
    company_id: int,
    token_version: int,
) -> tuple[str, int]:
    """Return (token, expires_in_seconds)."""
    settings = get_hr_auth_settings()
    now = datetime.now(timezone.utc)
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "cid": company_id,
        "tv": token_version,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expires_in


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a token. Raises jwt.PyJWTError on any problem."""
    settings = get_hr_auth_settings()
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["sub", "exp", "iat", "type"]},
    )
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("wrong token type")
    return payload
