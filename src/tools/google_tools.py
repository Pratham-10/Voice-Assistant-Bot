import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from src.config import google_credentials_path

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send'
]

def get_google_credentials():
    """
    Retrieves or generates Google API OAuth2 credentials.
    Saves/loads token.json locally for maximum privacy.
    """
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print(f"Error loading token.json: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists(google_credentials_path):
                print(f"\n[Google API Info] '{google_credentials_path}' not found.")
                print("To use Calendar/Gmail, download your OAuth 2.0 Credentials JSON from Google Cloud Console,")
                print("place it in the project root, and rename it to 'credentials.json'.")
                return None

            try:
                flow = InstalledAppFlow.from_client_secrets_file(google_credentials_path, SCOPES)
                print("\n" + "="*80)
                print("[Action Required] Starting Google Calendar & Gmail authorization.")
                print("A browser window will open asking you to sign in with your Google account.")
                print("If the browser does not open automatically, please click or copy/paste")
                print("the link generated below into your web browser.")
                print("="*80 + "\n")
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                print("\n[Google API Info] Authorization successful! Saved token.json locally.\n")
            except Exception as e:
                print(f"Failed to complete Google OAuth authorization flow: {e}")
                return None
    return creds

def get_calendar_timezone(service) -> str:
    """Helper to retrieve the user's primary calendar timezone, defaulting to Asia/Kolkata."""
    try:
        calendar_info = service.calendars().get(calendarId='primary').execute()
        return calendar_info.get('timeZone', 'Asia/Kolkata')
    except Exception as e:
        print(f"Failed to retrieve calendar timezone: {e}")
        return 'Asia/Kolkata'

def list_calendar_events(max_results: int = 5) -> str:
    """
    Lists the upcoming calendar events from Google Calendar.
    
    Args:
        max_results: The maximum number of events to return. Default is 5.
        
    Returns:
        A text summary of the events or an error message.
    """
    creds = get_google_credentials()
    if not creds:
        return "Google Calendar integration is not authorized. Please make sure credentials.json is present and sign in."

    try:
        service = build('calendar', 'v3', credentials=creds)
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=now,
            maxResults=max_results, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events:
            return "No upcoming events found in your Google Calendar."
            
        summary = "Here are your upcoming calendar events:\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary += f"- {event.get('summary', 'No Title')} on {start}\n"
        return summary
    except Exception as e:
        print(f"Google Calendar list error: {e}")
        return f"Failed to retrieve Google Calendar events: {e}"

def create_calendar_event(summary: str, start_time: str, duration_minutes: int = 30) -> str:
    """
    Creates a new event on Google Calendar, adjusting dynamically to the user's calendar timezone.
    
    Args:
        summary: The title/summary of the event.
        start_time: ISO-8601 string of the start time (e.g. '2026-07-07T14:00:00').
        duration_minutes: The duration of the event in minutes. Default is 30.
        
    Returns:
        Confirmation message or error message.
    """
    creds = get_google_credentials()
    if not creds:
        return "Google Calendar integration is not authorized. Please check your credentials.json configuration."

    try:
        service = build('calendar', 'v3', credentials=creds)
        user_timezone = get_calendar_timezone(service)
        
        from datetime import datetime, timedelta
        # Parse start time and compute end time
        try:
            start_dt = datetime.fromisoformat(start_time)
        except ValueError:
            try:
                start_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
                
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        # Format as standard ISO strings for API
        start_str = start_dt.isoformat()
        end_str = end_dt.isoformat()
        
        event_body = {
            'summary': summary,
            'start': {
                'dateTime': start_str,
                'timeZone': user_timezone,
            },
            'end': {
                'dateTime': end_str,
                'timeZone': user_timezone,
            },
        }
        
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        return f"Successfully created event '{summary}' on {start_time} in {user_timezone} timezone (Link: {event.get('htmlLink')})."
    except Exception as e:
        print(f"Google Calendar event creation error: {e}")
        return f"Failed to create Google Calendar event: {e}"

def delete_calendar_event(summary: str) -> str:
    """
    Deletes a calendar event by searching for its title/summary.
    
    Args:
        summary: The title/summary of the event to delete.
        
    Returns:
        A confirmation message or error message.
    """
    creds = get_google_credentials()
    if not creds:
        return "Google Calendar integration is not authorized."

    try:
        service = build('calendar', 'v3', credentials=creds)
        # Search for events matching the title
        events_result = service.events().list(
            calendarId='primary',
            q=summary,
            maxResults=5,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events:
            return f"No events found matching the title '{summary}'."
            
        # Delete the first matching event
        event_to_delete = events[0]
        event_id = event_to_delete['id']
        event_title = event_to_delete.get('summary', 'Untitled')
        event_start = event_to_delete['start'].get('dateTime', event_to_delete['start'].get('date'))
        
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return f"Successfully deleted the event '{event_title}' scheduled for {event_start}."
    except Exception as e:
        print(f"Google Calendar event deletion error: {e}")
        return f"Failed to delete Google Calendar event: {e}"

def reschedule_calendar_event(summary: str, new_start_time: str, duration_minutes: int = 30) -> str:
    """
    Reschedules an existing calendar event to a new start time.
    
    Args:
        summary: The title/summary of the event to reschedule.
        new_start_time: ISO-8601 string of the new start time (e.g. '2026-07-07T15:00:00').
        duration_minutes: The duration of the event in minutes. Default is 30.
        
    Returns:
        A confirmation message or error message.
    """
    creds = get_google_credentials()
    if not creds:
        return "Google Calendar integration is not authorized."

    try:
        service = build('calendar', 'v3', credentials=creds)
        user_timezone = get_calendar_timezone(service)
        
        # Search for events matching the title
        events_result = service.events().list(
            calendarId='primary',
            q=summary,
            maxResults=5,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events:
            return f"No events found matching the title '{summary}'."
            
        event_to_update = events[0]
        event_id = event_to_update['id']
        event_title = event_to_update.get('summary', 'Untitled')
        
        from datetime import datetime, timedelta
        # Parse new start time and compute new end time
        try:
            start_dt = datetime.fromisoformat(new_start_time)
        except ValueError:
            try:
                start_dt = datetime.strptime(new_start_time, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                start_dt = datetime.strptime(new_start_time, "%Y-%m-%d %H:%M")
                
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        start_str = start_dt.isoformat()
        end_str = end_dt.isoformat()
        
        # Update start and end time fields
        event_to_update['start'] = {
            'dateTime': start_str,
            'timeZone': user_timezone
        }
        event_to_update['end'] = {
            'dateTime': end_str,
            'timeZone': user_timezone
        }
        
        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event_to_update
        ).execute()
        
        return f"Successfully rescheduled '{event_title}' to {new_start_time} in {user_timezone} timezone."
    except Exception as e:
        print(f"Google Calendar event update error: {e}")
        return f"Failed to reschedule Google Calendar event: {e}"

def send_gmail(to_email: str, subject: str, message_body: str) -> str:
    """
    Sends an email using the authorized Gmail account.
    
    Args:
        to_email: The recipient's email address.
        subject: The subject line of the email.
        message_body: The body content of the email.
        
    Returns:
        Success or failure message.
    """
    creds = get_google_credentials()
    if not creds:
        return "Gmail integration is not authorized. Please make sure credentials.json is present."

    try:
        service = build('gmail', 'v1', credentials=creds)
        
        message = MIMEText(message_body)
        message['to'] = to_email
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        send_result = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return f"Successfully sent email to {to_email} with subject '{subject}' (Message ID: {send_result.get('id')})."
    except Exception as e:
        print(f"Gmail send error: {e}")
        return f"Failed to send email to {to_email}: {e}"
