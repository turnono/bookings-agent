import os
import datetime
from typing import Optional, List
from google.oauth2 import service_account
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = [
          'https://www.googleapis.com/auth/calendar',]

# Path to your OAuth2 credentials file (downloaded from Google Cloud Console)
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), '../../sim-guide-agent-service-account.json')

def get_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    return service

def list_upcoming_events(max_results: int, calendar_id: str):
    """
    Lists the next max_results events on the specified calendar.
    Args:
        max_results (int): The maximum number of events to return.
        calendar_id (str): The calendar ID (email address of the calendar).
    """
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                          maxResults=max_results, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return [{
        'summary': event.get('summary'),
        'start': event['start'].get('dateTime', event['start'].get('date'))
    } for event in events]

def create_event(
    calendar_id: str,
    summary: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None,
    attendees: Optional[List[str]] = None
):
    """
    Create a new event on the specified Google Calendar.
    Args:
        calendar_id (str): The calendar ID (email address of the calendar).
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
        'start': {'dateTime': start_time},
        'end': {'dateTime': end_time},
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