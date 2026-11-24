from datetime import datetime, timezone


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


