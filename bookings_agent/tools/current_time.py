import datetime
import os
from zoneinfo import ZoneInfo


def current_time(zone: str = None) -> str:
    """Get the current time in a given timezone. Call to provide the user with the current time.
    
    Args:
        zone (str, optional): Timezone identifier. If None, uses BOOKING_TIMEZONE environment variable.
    """
    # Get timezone from environment variable if not provided
    if not zone:
        zone = os.getenv('BOOKING_TIMEZONE')
    
    try:
        tz = ZoneInfo(zone)
        return datetime.datetime.now(tz).isoformat()
    except Exception:
        return datetime.datetime.utcnow().isoformat()


def current_year() -> int:
    """Get the current year in the system timezone (from BOOKING_TIMEZONE environment variable).
    
    Returns:
        int: The current year as an integer
    """
    # Get timezone from environment variable
    zone = os.getenv('BOOKING_TIMEZONE')
    
    try:
        tz = ZoneInfo(zone)
        now = datetime.datetime.now(tz)
        current_year = now.year
        print(f"Current year from timezone {zone}: {current_year}")
        return current_year
    except Exception as e:
        print(f"Error getting current year: {str(e)}")
        now = datetime.datetime.utcnow()
        print(f"Falling back to UTC: {now.year}")
        return now.year


