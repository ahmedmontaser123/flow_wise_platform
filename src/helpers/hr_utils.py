from datetime import datetime, timezone
from typing import Annotated
from fastapi import Depends,HTTPException, status
from models.enums.hr_role_enum import HRRole
from models.db.flow_wise.schema import HRUser



def utcnow() -> datetime:
    """Timezone-aware UTC now (for timestamptz columns)."""
    return datetime.now(timezone.utc)


def utcnow_naive() -> datetime:
    """UTC now without tzinfo, for the existing `DateTime` (timestamp without
    time zone) columns such as hr_users.created_at and jobs.created_at.
    asyncpg refuses aware datetimes for those columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def like_pattern(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def clean_name(value: str | None) -> str | None:
    if value is None:
        return None
    value = " ".join(value.split())
    if not value:
        raise ValueError("Must not be empty")
    return value


def password_rules(value: str) -> str:
    # bcrypt only uses the first 72 bytes, so longer passwords are refused.
    if len(value.encode("utf-8")) > 72:
        raise ValueError("Password must be at most 72 bytes")
    if value.strip() != value:
        raise ValueError("Password must not start or end with spaces")
    if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
        raise ValueError("Password must contain at least one letter and one number")
    return value


def require_roles(*allowed: HRRole):
    """Dependency factory: allow only the given roles."""
    from dependencies import get_current_hr

    async def _checker(
        user: Annotated[HRUser, Depends(get_current_hr)],
    ) -> HRUser:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return user

    return _checker


