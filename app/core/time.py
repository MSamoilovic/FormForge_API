from datetime import UTC, datetime


def utcnow() -> datetime:
    """Current UTC time as a naive datetime (tzinfo stripped)."""
    return datetime.now(UTC).replace(tzinfo=None)
