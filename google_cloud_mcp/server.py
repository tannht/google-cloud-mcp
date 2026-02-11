from fastmcp import FastMCP
import os.path
import base64
import json
import threading
from urllib.parse import urlparse, parse_qs
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
AUTH_PORT = int(os.getenv('AUTH_PORT', '3838'))

mcp = FastMCP("Google Cloud MCP")

def get_credentials():
    creds = None
    token_json = os.getenv('GOOGLE_TOKEN_JSON')
    if token_json:
        try: creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)
        except: pass
    if (not creds or not creds.valid) and os.path.exists(TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

# --- AUTH PORTAL ---

_pending_flow = None

class AuthPortalHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        global _pending_flow
        redirect_uri = f"http://localhost:{AUTH_PORT}/callback"

        if self.path == '/':
            creds = get_credentials()
            ok = creds and creds.valid
            html = f"""<html><head><title>PubPug Google Portal</title></head>
            <body style='font-family:sans-serif;padding:50px;background:#f0f2f5;display:flex;justify-content:center'>
            <div style='max-width:500px;background:#fff;padding:40px;border-radius:15px;box-shadow:0 4px 20px rgba(0,0,0,.1);text-align:center'>
            <h1 style='color:#1a73e8'>PubPug Google MCP</h1>
            <p style='font-size:18px;color:{"#4CAF50" if ok else "#f44336"};font-weight:bold'>{"Authenticated" if ok else "Not Authenticated"}</p>
            <hr style='border:0;border-top:1px solid #eee;margin:20px 0'>
            <a href='/login' style='display:inline-block;padding:15px 30px;background:#1a73e8;color:#fff;text-decoration:none;border-radius:5px;font-weight:bold'>Authorize with Google</a>
            </div></body></html>"""
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode())

        elif self.path == '/login':
            if CLIENT_ID and CLIENT_SECRET:
                config = {"installed": {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
                           "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                           "token_uri": "https://oauth2.googleapis.com/token",
                           "redirect_uris": [redirect_uri]}}
                _pending_flow = InstalledAppFlow.from_client_config(config, SCOPES, redirect_uri=redirect_uri)
            else:
                _pending_flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE_PATH, SCOPES, redirect_uri=redirect_uri)
            auth_url, _ = _pending_flow.authorization_url(prompt='consent', access_type='offline')
            self.send_response(302)
            self.send_header('Location', auth_url)
            self.end_headers()

        elif self.path.startswith('/callback'):
            try:
                code = parse_qs(urlparse(self.path).query).get('code', [None])[0]
                if not code: raise ValueError("No authorization code received")
                if not _pending_flow: raise ValueError("No pending auth flow. Start from /login.")
                _pending_flow.fetch_token(code=code)
                with open(TOKEN_FILE_PATH, 'w') as f:
                    f.write(_pending_flow.credentials.to_json())
                html = """<html><body style='font-family:sans-serif;padding:50px;background:#f0f2f5;display:flex;justify-content:center'>
                <div style='max-width:500px;background:#fff;padding:40px;border-radius:15px;box-shadow:0 4px 20px rgba(0,0,0,.1);text-align:center'>
                <h1 style='color:#4CAF50'>Authenticated!</h1><p>Token saved. You can now use Google services through MCP.</p>
                <a href='/' style='display:inline-block;padding:10px 20px;background:#1a73e8;color:#fff;text-decoration:none;border-radius:5px;margin-top:15px'>Back to Portal</a>
                </div></body></html>"""
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode())
            except Exception as e:
                html = f"""<html><body style='font-family:sans-serif;padding:50px;background:#f0f2f5;display:flex;justify-content:center'>
                <div style='max-width:500px;background:#fff;padding:40px;border-radius:15px;box-shadow:0 4px 20px rgba(0,0,0,.1);text-align:center'>
                <h1 style='color:#f44336'>Error</h1><p>{e}</p>
                <a href='/login' style='display:inline-block;padding:10px 20px;background:#1a73e8;color:#fff;text-decoration:none;border-radius:5px;margin-top:15px'>Try Again</a>
                </div></body></html>"""
                self.send_response(500)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.encode())

def _start_portal():
    server = HTTPServer(('0.0.0.0', AUTH_PORT), AuthPortalHandler)
    print(f"Auth Portal running at http://localhost:{AUTH_PORT}")
    server.serve_forever()

threading.Thread(target=_start_portal, daemon=True).start()

# --- GMAIL TOOLS ---

@mcp.tool()
def get_account_info():
    """Get the email address of the currently authenticated Google account."""
    try:
        service = build('gmail', 'v1', credentials=get_credentials())
        profile = service.users().getProfile(userId='me').execute()
        return f"🐶 Authenticated as: {profile.get('emailAddress')} (Gâu!)"
    except Exception as e: return f"❌ Error: {e}"

@mcp.tool()
def create_gmail_label(name: str):
    """Create a new label in Gmail."""
    try:
        service = build('gmail', 'v1', credentials=get_credentials())
        label = {'name': name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
        res = service.users().labels().create(userId='me', body=label).execute()
        return f"✅ Label '{name}' created."
    except Exception as e: return str(e)

@mcp.tool()
def list_gmail_labels():
    """List all user labels in Gmail."""
    try:
        service = build('gmail', 'v1', credentials=get_credentials())
        res = service.users().labels().list(userId='me').execute()
        labels = [l['name'] for l in res.get('labels', []) if l['type'] == 'user']
        return "\n".join(labels) if labels else "No user labels found."
    except Exception as e: return str(e)

@mcp.tool()
def send_email(to: str, subject: str, body: str):
    """Send a simple email via Gmail."""
    try:
        service = build('gmail', 'v1', credentials=get_credentials())
        message = EmailMessage()
        message.set_content(body)
        message['To'], message['Subject'] = to, subject
        encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
        res = service.users().messages().send(userId="me", body={'raw': encoded}).execute()
        return f"✅ Email sent! ID: {res['id']}"
    except Exception as e: return str(e)

# --- CALENDAR TOOLS ---

@mcp.tool()
def list_calendar_events(max_results: int = 10, days_back: int = 0):
    """List events. Timezone: Asia/Ho_Chi_Minh."""
    try:
        service = build('calendar', 'v3', credentials=get_credentials())
        time_min = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + 'Z'
        res = service.events().list(calendarId='primary', timeMin=time_min,
                                    maxResults=max_results, singleEvents=True,
                                    orderBy='startTime').execute()
        events = res.get('items', [])
        if not events: return "No events found."
        return "\n".join([f"- {e['start'].get('dateTime', e['start'].get('date'))}: {e.get('summary')} (ID: {e.get('id')})" for e in events])
    except Exception as e: return str(e)

@mcp.tool()
def create_calendar_event(summary: str, start_time: str, end_time: str, description: str = ""):
    """Create a calendar event. format: YYYY-MM-DDTHH:MM (VN Time)."""
    try:
        service = build('calendar', 'v3', credentials=get_credentials())
        event = {
            'summary': summary, 'description': description,
            'start': {'dateTime': f"{start_time}:00", 'timeZone': 'Asia/Ho_Chi_Minh'},
            'end': {'dateTime': f"{end_time}:00", 'timeZone': 'Asia/Ho_Chi_Minh'},
        }
        res = service.events().insert(calendarId='primary', body=event).execute()
        return f"✅ Event created: {res.get('htmlLink')}"
    except Exception as e: return str(e)

# --- DRIVE TOOLS ---

@mcp.tool()
def search_drive(query: str):
    """Search for files in Google Drive."""
    try:
        service = build('drive', 'v3', credentials=get_credentials())
        res = service.files().list(q=query, fields='files(id, name, mimeType)').execute()
        items = res.get('files', [])
        return "\n".join([f"- {item['name']} ({item['id']})" for item in items]) if items else "No files found."
    except Exception as e: return str(e)

if __name__ == "__main__":
    mcp.run()
