from fastmcp import FastMCP
import os.path
import base64
import json
import threading
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

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

TOKEN_JSON_ENV = os.getenv('GOOGLE_TOKEN_JSON')
TOKEN_FILE_PATH = os.getenv('GOOGLE_TOKEN_PATH', '.token.json')
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
CRED_FILE_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')

mcp = FastMCP("Google Cloud MCP")

# Global variables for auth flow
auth_flow = None
auth_url = None

def get_credentials():
    creds = None
    if TOKEN_JSON_ENV:
        try:
            creds = Credentials.from_authorized_user_info(json.loads(TOKEN_JSON_ENV), SCOPES)
        except: pass

    if (not creds or not creds.valid) and os.path.exists(TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, SCOPES)
    
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        
    return creds

@mcp.tool()
def get_auth_link():
    """Check authentication status and return authorization URL if needed."""
    creds = get_credentials()
    if creds and creds.valid:
        return "✅ PubPug is already authenticated and ready to go! Gâu gâu!"
    
    global auth_flow, auth_url
    if CLIENT_ID and CLIENT_SECRET:
        client_config = {"installed": {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "redirect_uris": ["http://localhost:3000"]}}
        auth_flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    else:
        if not os.path.exists(CRED_FILE_PATH):
            return "❌ Missing Credentials! Please provide GOOGLE_CLIENT_ID/SECRET or credentials.json file."
        auth_flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE_PATH, SCOPES)
    
    # Generate URL
    auth_url, _ = auth_flow.authorization_url(prompt='consent', access_type='offline')
    
    # Start a local server in a separate thread to catch the callback
    def run_server():
        creds = auth_flow.run_local_server(port=3000, open_browser=False)
        with open(TOKEN_FILE_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
        print(f"✅ Token saved to {TOKEN_FILE_PATH}")

    threading.Thread(target=run_server, daemon=True).start()
    
    return f"🐶 PubPug needs your permission! \n\n1. Please visit this URL to authorize: \n{auth_url} \n\n2. After authorizing, I will automatically detect the token. Just wait a few seconds and try calling me again! Gâu!"

# --- GMAIL TOOLS ---

def get_gmail_service():
    creds = get_credentials()
    if not creds: raise Exception("PubPug is not authenticated. Please call 'get_auth_link' tool first.")
    return build('gmail', 'v1', credentials=creds)

@mcp.tool()
def create_gmail_label(name: str):
    """Create a new label in Gmail."""
    try:
        service = get_gmail_service()
        label = {'name': name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
        res = service.users().labels().create(userId='me', body=label).execute()
        return f"✅ Label '{name}' created (ID: {res['id']})"
    except Exception as e: return str(e)

@mcp.tool()
def list_gmail_labels():
    """List all user labels in Gmail."""
    try:
        service = get_gmail_service()
        res = service.users().labels().list(userId='me').execute()
        labels = [l['name'] for l in res.get('labels', []) if l['type'] == 'user']
        return "\n".join(labels) if labels else "No user labels found."
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

@mcp.tool()
def clean_spam():
    """Delete all messages in the Spam folder."""
    try:
        service = get_gmail_service()
        res = service.users().messages().list(userId='me', labelIds=['SPAM']).execute()
        messages = res.get('messages', [])
        if not messages: return "Spam folder is clean."
        for msg in messages: service.users().messages().delete(userId='me', id=msg['id']).execute()
        return f"✅ Cleaned {len(messages)} spam emails."
    except Exception as e: return str(e)

if __name__ == "__main__":
    mcp.run()
