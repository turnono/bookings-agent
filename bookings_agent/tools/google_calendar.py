import os
import datetime
import re
from typing import Optional, List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from zoneinfo import ZoneInfo

# If modifying these SCOPES, delete the file token.json.
SCOPES = [
          'https://www.googleapis.com/auth/calendar',]

# Path to your OAuth2 credentials file (downloaded from Google Cloud Console)
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), '../../taajirah-agents-service-account.json')
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
                  Note: Adding attendees requires Domain-Wide Delegation for service accounts.
                  If you encounter a 403 error, try without attendees.
    Returns:
        dict: Created event's summary and htmlLink.
    """
    service = get_calendar_service()
    
    # Parse the start time to extract date information for clarity
    start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    
    # Add year to the summary for clarity
    if not summary.endswith(str(start_dt.year)):
        summary = f"{summary} ({start_dt.year})"
        
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': time_zone},
        'end': {'dateTime': end_time, 'timeZone': time_zone},
    }
    
    # Format the description to include the date
    desc_parts = []
    if description:
        desc_parts.append(description)
    
    # Add date in a clear format that shows the year
    date_str = start_dt.strftime("%A, %B %d, %Y")
    time_str = f"{start_dt.strftime('%H:%M')}-{datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00')).strftime('%H:%M')}"
    desc_parts.append(f"Date: {date_str}")
    desc_parts.append(f"Time: {time_str}")
    
    event['description'] = "\n\n".join(desc_parts)
    
    # First try to create the event with attendees if provided
    event_with_attendees = event.copy()
    if attendees:
        event_with_attendees['attendees'] = [{'email': email} for email in attendees]
        
    try:
        # Try to create event with attendees first
        if attendees:
            created_event = service.events().insert(calendarId=calendar_id, body=event_with_attendees).execute()
        else:
            created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
            
        return {
            'summary': created_event.get('summary'),
            'htmlLink': created_event.get('htmlLink')
        }
    except Exception as e:
        # If failed and has attendees, try again without attendees
        if attendees and "Service accounts cannot invite attendees" in str(e):
            print(f"Warning: Service account cannot add attendees without Domain-Wide Delegation. Creating event without attendees.")
            # Create without attendees
            created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
            
            # Add note about attendees in description
            if description:
                event['description'] = f"{description}\n\nCould not automatically add attendees. Please manually invite: {', '.join(attendees)}"
            else:
                event['description'] = f"Could not automatically add attendees. Please manually invite: {', '.join(attendees)}"
                
            # Update the event with the new description
            service.events().update(calendarId=calendar_id, eventId=created_event['id'], body=event).execute()
            
            return {
                'summary': created_event.get('summary'),
                'htmlLink': created_event.get('htmlLink'),
                'attendees_warning': "Service account cannot add attendees. You'll need to add them manually or enable Domain-Wide Delegation."
            }
        else:
            # If it's a different error, re-raise
            raise

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


def get_all_available_slots(
    slot_duration_minutes: int = 30,
    weeks_ahead: int = 3,
    start_from_date_iso: str = ""
) -> dict:
    """
    Find all available time slots for the next specified weeks.
    
    Args:
        slot_duration_minutes (int): Duration of each slot in minutes (default 30)
        weeks_ahead (int): Number of weeks to look ahead (default 3)
        start_from_date_iso (str, optional): If provided, only show slots from this date forward (ISO format)
        
    Returns:
        dict: Dictionary containing all slots, slots grouped by date, and total count
    """
    # Get the current date/time in the correct timezone
    tz = ZoneInfo(time_zone)
    now = datetime.datetime.now(tz)
    
    print(f"Current datetime in {time_zone}: {now.isoformat()}")
    
    # If start_from_date is not provided, calculate next Tuesday (May 13, 2025)
    if not start_from_date_iso:
        # Find next Tuesday (weekday 1)
        days_until_next_tuesday = (1 - now.weekday()) % 7
        if days_until_next_tuesday == 0:  # If today is Tuesday, use next week
            days_until_next_tuesday = 7
            
        # Calculate the date for next Tuesday
        next_tuesday = now + datetime.timedelta(days=days_until_next_tuesday)
        
        # Set to midnight of next Tuesday
        start_date = datetime.datetime(
            next_tuesday.year, next_tuesday.month, next_tuesday.day, 0, 0, 0, 
            tzinfo=tz
        )
        print(f"Starting from next Tuesday: {start_date.strftime('%A, %B %d, %Y')}")
    else:
        # Parse the provided ISO date string
        try:
            start_date = datetime.datetime.fromisoformat(start_from_date_iso)
            # Ensure timezone is set
            if start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=tz)
            print(f"Starting from provided date: {start_date.strftime('%A, %B %d, %Y')}")
        except ValueError:
            # If parsing fails, fall back to next Tuesday
            days_until_next_tuesday = (1 - now.weekday()) % 7
            if days_until_next_tuesday == 0:
                days_until_next_tuesday = 7
            next_tuesday = now + datetime.timedelta(days=days_until_next_tuesday)
            start_date = datetime.datetime(
                next_tuesday.year, next_tuesday.month, next_tuesday.day, 0, 0, 0, 
                tzinfo=tz
            )
            print(f"Invalid date format, falling back to next Tuesday: {start_date.strftime('%A, %B %d, %Y')}")
    
    # Set to X weeks from the start date at midnight
    end_date = start_date + datetime.timedelta(weeks=weeks_ahead)
    
    print(f"Searching for slots from {start_date.isoformat()} to {end_date.isoformat()}")
    
    # Format dates to ISO strings with Z for API calls
    start_time_window = start_date.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time_window = end_date.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Get calendar service
    service = get_calendar_service()
    
    # Fetch existing events in the date range
    existing_events = service.events().list(
        calendarId=calendar_id,
        timeMin=start_time_window,
        timeMax=end_time_window,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    # Create a list of busy time slots from existing events
    busy_slots = []
    for event in existing_events.get('items', []):
        if 'dateTime' in event['start'] and 'dateTime' in event['end']:
            start = datetime.datetime.fromisoformat(
                event['start']['dateTime'].replace('Z', '+00:00')
            ).astimezone(tz)
            end = datetime.datetime.fromisoformat(
                event['end']['dateTime'].replace('Z', '+00:00')
            ).astimezone(tz)
            busy_slots.append((start, end))
    
    print(f"Found {len(busy_slots)} existing events in calendar")
    
    # Generate all possible slots for Tuesdays and Thursdays
    all_slots = []
    current_date = start_date
    while current_date < end_date:
        # Only consider Tuesdays (1) and Thursdays (3)
        if current_date.weekday() in [1, 3]:
            # Add slots at 18:00 and 18:30
            for hour, minute in [(18, 0), (18, 30)]:
                slot_start = current_date.replace(hour=hour, minute=minute)
                slot_end = slot_start + datetime.timedelta(minutes=slot_duration_minutes)
                
                # Skip slots that are in the past
                if slot_start < now:
                    continue
                
                # Check if slot overlaps with any existing event
                is_available = True
                for busy_start, busy_end in busy_slots:
                    # Check for overlap
                    if max(slot_start, busy_start) < min(slot_end, busy_end):
                        is_available = False
                        print(f"Slot {slot_start.strftime('%Y-%m-%d %H:%M')} is busy")
                        break
                        
                if is_available:
                    # Convert to UTC for storage
                    slot_start_utc = slot_start.astimezone(datetime.timezone.utc)
                    slot_end_utc = slot_end.astimezone(datetime.timezone.utc)
                    
                    all_slots.append({
                        "start": slot_start_utc.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        "end": slot_end_utc.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        "display": f"{slot_start.strftime('%A, %d %b %Y, %H:%M')}-{slot_end.strftime('%H:%M')}",
                        "date": slot_start.strftime("%d %b %Y"),
                        "day": slot_start.strftime("%A"),
                        "time": f"{slot_start.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}"
                    })
                    print(f"Added available slot: {slot_start.strftime('%A, %d %b %Y, %H:%M')}-{slot_end.strftime('%H:%M')}")
        
        # Move to next day
        current_date = current_date + datetime.timedelta(days=1)
    
    # Group slots by date for easier display
    grouped_slots = {}
    for slot in all_slots:
        date = slot['date']
        if date not in grouped_slots:
            grouped_slots[date] = []
        grouped_slots[date].append(slot)
    
    # Create a formatted display version for easy presentation to users
    formatted_display = []
    for date, slots in grouped_slots.items():
        # Extract day name and full date from the first slot
        if slots:
            first_slot = slots[0]
            # Parse the date string to create a full date display
            date_parts = first_slot['date'].split()
            day = first_slot['day']
            
            # Create a better formatted date: e.g., "Tuesday, May 13, 2025"
            month_name = datetime.datetime.strptime(date_parts[1], '%b').strftime('%B')
            formatted_date = f"**{day}, {month_name} {date_parts[0]}, {date_parts[2]}**"
            
            # Extract all times for this date
            times = [slot['time'] for slot in slots]
            time_str = " and ".join(times)
            
            # Create the full entry
            formatted_display.append(f"{formatted_date} at {time_str}")
    
    print(f"Total available slots: {len(all_slots)}")
            
    return {
        'all_slots': all_slots,
        'grouped_by_date': grouped_slots,
        'total_slots': len(all_slots),
        'formatted_display': formatted_display
    } 