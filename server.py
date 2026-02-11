from fastmcp import FastMCP
import os.path
import base64
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/presentations'
]

TOKEN_FILE_PATH = os.getenv('GOOGLE_TOKEN_PATH', '.token.json')
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
CRED_FILE_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')

mcp = FastMCP("Google Cloud MCP")

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    return creds

def get_gmail_service():
    return build('gmail', 'v1', credentials=get_credentials())

def get_drive_service():
    return build('drive', 'v3', credentials=get_credentials())

def get_calendar_service():
    return build('calendar', 'v3', credentials=get_credentials())

# --- GMAIL TOOLS ---

@mcp.tool()
def create_gmail_label(name: str):
    """Create a new label in Gmail."""
    try:
        service = get_gmail_service()
        label = {'name': name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
        res = service.users().labels().create(userId='me', body=label).execute()
        return f"✅ Label '{name}' created."
    except Exception as e: return str(e)

@mcp.tool()
def list_gmail_labels():
    """List all user labels in Gmail."""
    try:
        service = get_gmail_service()
        res = service.users().labels().list(userId='me').execute()
        labels = [l['name'] for l in res.get('labels', []) if l['type'] == 'user']
        return "\n".join(labels) if labels else "No labels."
    except Exception as e: return str(e)

@mcp.tool()
def send_email(to: str, subject: str, body: str):
    """Send a simple email via Gmail."""
    try:
        service = get_gmail_service()
        message = EmailMessage()
        message.set_content(body)
        message['To'], message['Subject'] = to, subject
        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
        res = service.users().messages().send(userId="me", body={'raw': encoded}).execute()
        return f"✅ Email sent! ID: {res['id']}"
    except Exception as e: return str(e)

# --- CALENDAR TOOLS ---

@mcp.tool()
def list_calendar_events(max_results: int = 10):
    """List the next upcoming events from the primary calendar."""
    try:
        service = get_calendar_service()
        now = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=max_results, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events: return "No upcoming events found."
        output = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            output.append(f"- {start}: {event.get('summary')} (ID: {event.get('id')})")
        return "\n".join(output)
    except Exception as e: return f"❌ Error: {e}"

@mcp.tool()
def create_calendar_event(summary: str, description: str, start_time: str, end_time: str):
    """Create a new calendar event. Times must be in ISO format (e.g., 2026-02-11T20:00:00)."""
    try:
        service = get_calendar_service()
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': f"{start_time}Z", 'timeZone': 'UTC'},
            'end': {'dateTime': f"{end_time}Z", 'timeZone': 'UTC'},
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"✅ Event created: {event.get('htmlLink')}"
    except Exception as e: return f"❌ Error: {e}"

@mcp.tool()
def delete_calendar_event(event_id: str):
    """Delete a calendar event by its ID."""
    try:
        service = get_calendar_service()
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return "✅ Event deleted successfully."
    except Exception as e: return f"❌ Error: {e}"

# --- DRIVE TOOLS ---

@mcp.tool()
def search_drive(query: str):
    """Search for files in Google Drive."""
    try:
        service = get_drive_service()
        res = service.files().list(q=query, fields='files(id, name, mimeType)').execute()
        items = res.get('files', [])
        if not items: return "No files found."
        return "\n".join([f"- {item['name']} ({item['id']})" for item in items])
    except Exception as e: return str(e)

if __name__ == "__main__":
    mcp.run()
