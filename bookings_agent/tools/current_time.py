import datetime
from zoneinfo import ZoneInfo


def current_time(zone: str) -> str:
    """Get the current time in a given timezone. Call to provide the user with the current time. Args: zone (str)."""
    try:
        tz = ZoneInfo(zone)
        return datetime.datetime.now(tz).isoformat()
    except Exception:
        return datetime.datetime.utcnow().isoformat()


