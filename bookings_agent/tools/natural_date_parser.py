import dateparser
from typing import Optional
from datetime import datetime

def parse_natural_date(date_str: str, settings: Optional[dict] = None) -> Optional[datetime]:
    """
    Parse a natural language date string into a datetime object using dateparser.

    Args:
        date_str (str): The natural language date string (e.g., 'tomorrow', 'next week', 'in 3 days').
        settings (dict, optional): Optional settings for dateparser (e.g., {'PREFER_DATES_FROM': 'future'}).

    Returns:
        datetime or None: The parsed datetime object, or None if parsing fails.
    """
    if not date_str or not isinstance(date_str, str):
        return None
    result = dateparser.parse(date_str, settings=settings)
    return result 