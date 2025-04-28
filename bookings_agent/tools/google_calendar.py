import os
import datetime
import re
from typing import Optional, List
from google.oauth2 import service_account
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = [
          'https://www.googleapis.com/auth/calendar',]

# Path to your OAuth2 credentials file (downloaded from Google Cloud Console)
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), '../../sim-guide-agent-service-account.json')
calendar_id = os.getenv('BOOKING_CALENDAR_ID')
time_zone = os.getenv('BOOKING_TIMEZONE')

if not calendar_id:
    raise RuntimeError("BOOKING_CALENDAR_ID environment variable is not set!")
if not time_zone:
    raise RuntimeError("BOOKING_TIMEZONE environment variable is not set!")

def get_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    return service

def list_upcoming_events(max_results: int):
    """
    Lists the next max_results events on the specified calendar.
    Args:
        max_results (int): The maximum number of events to return.
    """
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                          maxResults=max_results, singleEvents=True,
                                          orderBy='startTime',
                                          timeZone=time_zone).execute()
    events = events_result.get('items', [])
    return [{
        'summary': event.get('summary'),
        'start': event['start'].get('dateTime', event['start'].get('date'))
    } for event in events]

def create_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None,
    attendees: Optional[List[str]] = None
):
    """
    Create a new event on the specified Google Calendar.
    Args:
        summary (str): The event title.
        start_time (str): RFC3339 start time (e.g., '2025-04-28T10:00:00-07:00').
        end_time (str): RFC3339 end time (e.g., '2025-04-28T11:00:00-07:00').
        description (str, optional): Event description.
        attendees (List[str], optional): List of attendee email addresses.
    Returns:
        dict: Created event's summary and htmlLink.
    """
    service = get_calendar_service()
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': time_zone},
        'end': {'dateTime': end_time, 'timeZone': time_zone},
    }
    if description:
        event['description'] = description
    if attendees:
        event['attendees'] = [{'email': email} for email in attendees]
    created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    return {
        'summary': created_event.get('summary'),
        'htmlLink': created_event.get('htmlLink')
    }

def ensure_rfc3339_z(dt: str) -> str:
    # If already ends with Z, return as is
    if dt.endswith("Z"):
        return dt
    # If has a timezone offset, convert to UTC and add Z
    match = re.match(r"(.*)([+-]\d{2}:\d{2})$", dt)
    if match:
        dt_obj = datetime.datetime.fromisoformat(dt)
        return dt_obj.astimezone(datetime.timezone.utc).replace(tzinfo=None).isoformat(timespec='seconds') + "Z"
    # If no timezone, just add Z if it looks like a datetime
    if "T" in dt:
        return dt + "Z"
    raise ValueError(f"Invalid datetime string: {dt}")

def get_available_time_slots(
    start_time_window: str,
    end_time_window: str,
    slot_duration_minutes: int = 30,
    min_gap_minutes: int = 0
) -> List[dict]:
    """
    Find available time slots in the given window using Google Calendar's free/busy API.
    Args:
        start_time_window (str): ISO timestamp (start of search window)
        end_time_window (str): ISO timestamp (end of search window)
        slot_duration_minutes (int): Duration of each slot in minutes
        min_gap_minutes (int): Minimum gap between slots in minutes
    Returns:
        List[dict]: List of available slots as {"start": ..., "end": ...}
    """
    start_time_window = ensure_rfc3339_z(start_time_window)
    end_time_window = ensure_rfc3339_z(end_time_window)
    assert calendar_id, "calendar_id is empty"
    assert start_time_window.endswith("Z"), "start_time_window must end with Z"
    assert end_time_window.endswith("Z"), "end_time_window must end with Z"
    service = get_calendar_service()
    body = {
        "timeMin": start_time_window,
        "timeMax": end_time_window,
        "timeZone": time_zone,
        "items": [{"id": calendar_id}]
    }
    print("Request body for freebusy:", body)
    print("calendar_id:", calendar_id)
    busy_times = service.freebusy().query(body=body).execute()["calendars"][calendar_id]["busy"]
    # Convert busy times to datetime
    busy_periods = [
        (datetime.datetime.fromisoformat(b["start"].replace("Z", "+00:00")),
         datetime.datetime.fromisoformat(b["end"].replace("Z", "+00:00")))
        for b in busy_times
    ]
    # Sort busy periods
    busy_periods.sort()
    # Build list of free periods
    window_start = datetime.datetime.fromisoformat(start_time_window.replace("Z", "+00:00"))
    window_end = datetime.datetime.fromisoformat(end_time_window.replace("Z", "+00:00"))
    free_periods = []
    last_end = window_start
    for start, end in busy_periods:
        if last_end < start:
            free_periods.append((last_end, start))
        last_end = max(last_end, end)
    if last_end < window_end:
        free_periods.append((last_end, window_end))
    # Find slots in free periods
    slots = []
    slot_delta = datetime.timedelta(minutes=slot_duration_minutes)
    gap_delta = datetime.timedelta(minutes=min_gap_minutes)
    for free_start, free_end in free_periods:
        slot_start = free_start
        while slot_start + slot_delta <= free_end:
            slot_end = slot_start + slot_delta
            slots.append({
                "start": slot_start.isoformat().replace("+00:00", "Z"),
                "end": slot_end.isoformat().replace("+00:00", "Z")
            })
            slot_start = slot_end + gap_delta
    return slots 