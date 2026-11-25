
from helpers import get_settings
from datetime import datetime, timedelta, timezone
from models.enums import HRRole
from typing import Any
import jwt


def create_access_token(
    *,
    hr_id: int,
    role: HRRole,
    company_id: int,
    token_version: int,
) -> tuple[str, int]:

    if hr_id <= 0 or company_id <= 0 or token_version < 0:
        raise ValueError("Invalid token data")

    settings = get_settings()

    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    if expires_in <= 0:
        raise ValueError("Token expiration must be positive")

    now = datetime.now(timezone.utc)

    payload: dict[str, Any] = {
        "sub": str(hr_id),
        "role": role.value,
        "cid": company_id,
        "tv": token_version,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token, expires_in

def decode_access_token(token: str) -> dict[str, Any]:

    settings = get_settings()

    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={
            "require": [
                "sub",
                "role",
                "cid",
                "tv",
                "iat",
                "exp",
                "type",
            ]
        },
    )

    if payload["type"] != "access":
        raise jwt.InvalidTokenError("Invalid token type")

    if (
        not isinstance(payload["sub"], str)
        or not payload["sub"].isdigit()
        or int(payload["sub"]) <= 0
        or not isinstance(payload["role"], str)
        or payload["role"] not in {r.value for r in HRRole}
        or type(payload["cid"]) is not int
        or payload["cid"] <= 0
        or type(payload["tv"]) is not int
        or payload["tv"] < 0
        or type(payload["iat"]) is not int
        or type(payload["exp"]) is not int
    ):
        raise jwt.InvalidTokenError("Invalid token claims")

    return payload
