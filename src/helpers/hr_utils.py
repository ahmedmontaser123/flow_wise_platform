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
