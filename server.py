from fastmcp import FastMCP
import os.path
import base64
import json
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fixed Scopes for full functionality
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

# Smart Configuration
TOKEN_JSON_ENV = os.getenv('GOOGLE_TOKEN_JSON') # Direct JSON string from env
TOKEN_FILE_PATH = os.getenv('GOOGLE_TOKEN_PATH', '.token.json') # Default path
CRED_FILE_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

mcp = FastMCP("Google Cloud MCP")

def get_credentials():
    creds = None
    
    # 1. Try loading from GOOGLE_TOKEN_JSON environment variable (Highest priority)
    if TOKEN_JSON_ENV:
        try:
            token_data = json.loads(TOKEN_JSON_ENV)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            print("🐶 Using Token from environment variable.")
        except Exception as e:
            print(f"⚠️ Error parsing GOOGLE_TOKEN_JSON: {e}")

    # 2. Try loading from token file if env is missing or invalid
    if (not creds or not creds.valid) and os.path.exists(TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, SCOPES)
        print(f"🐶 Using Token from file: {TOKEN_FILE_PATH}")
    
    # 3. Handle expired/missing credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Token expired. Refreshing...")
            creds.refresh(Request())
        else:
            print("🔑 No valid credentials found. Starting authentication flow...")
            # Prefer Direct Client ID/Secret over JSON file
            if CLIENT_ID and CLIENT_SECRET:
                client_config = {
                    "installed": {
                        "client_id": CLIENT_ID,
                        "client_secret": CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost"]
                    }
                }
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            else:
                if not os.path.exists(CRED_FILE_PATH):
                    raise FileNotFoundError(f"❌ Missing credentials! Set GOOGLE_CLIENT_ID/SECRET or provide {CRED_FILE_PATH}")
                flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE_PATH, SCOPES)
            
            # Run local server for initial auth
            creds = flow.run_local_server(port=0, open_browser=False)
            
            # Save token to file for persistence (unless instructed otherwise)
            with open(TOKEN_FILE_PATH, 'w') as token:
                token.write(creds.to_json())
            print(f"✅ Token saved to {TOKEN_FILE_PATH}. Keep this safe!")
            
    return creds

def get_gmail_service():
    creds = get_credentials()
    return build('gmail', 'v1', credentials=creds)

def get_drive_service():
    creds = get_credentials()
    return build('drive', 'v3', credentials=creds)

# --- TOOLS ---

@mcp.tool()
def create_gmail_label(name: str):
    """Create a new label in Gmail."""
    try:
        service = get_gmail_service()
        label = {'name': name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
        created_label = service.users().labels().create(userId='me', body=label).execute()
        return f"✅ Label '{name}' created (ID: {created_label['id']})"
    except HttpError as error:
        return f"❌ Error: {error}"

@mcp.tool()
def list_gmail_labels():
    """List all user labels in Gmail."""
    try:
        service = get_gmail_service()
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        user_labels = [l['name'] for l in labels if l['type'] == 'user']
        return "\n".join(user_labels) if user_labels else "No user labels found."
    except HttpError as error:
        return f"❌ Error: {error}"

@mcp.tool()
def create_gmail_filter(from_email: str, label_name: str, archive: bool = False):
    """Create a filter to automatically label incoming emails from a specific sender."""
    try:
        service = get_gmail_service()
        labels_results = service.users().labels().list(userId='me').execute()
        labels = labels_results.get('labels', [])
        label_id = next((l['id'] for l in labels if l['name'] == label_name), None)
        if not label_id: return f"❌ Error: Label '{label_name}' not found."
        
        filter_body = {
            'criteria': {'from': from_email},
            'action': {'addLabelIds': [label_id], 'removeLabelIds': ['INBOX'] if archive else []}
        }
        result = service.users().settings().filters().create(userId='me', body=filter_body).execute()
        return f"✅ Filter created for '{from_email}' (ID: {result['id']})"
    except HttpError as error:
        return f"❌ Error: {error}"

@mcp.tool()
def batch_label_emails(query: str, label_name: str):
    """Search for emails and apply a label to all matching messages."""
    try:
        service = get_gmail_service()
        labels_results = service.users().labels().list(userId='me').execute()
        labels = labels_results.get('labels', [])
        label_id = next((l['id'] for l in labels if l['name'] == label_name), None)
        if not label_id: return f"❌ Error: Label '{label_name}' not found."
        
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        if not messages: return f"No emails found matching query '{query}'."
        
        for msg in messages:
            service.users().messages().batchModify(userId='me', body={'ids': [msg['id']], 'addLabelIds': [label_id]}).execute()
        return f"✅ Labeled {len(messages)} emails as '{label_name}'."
    except HttpError as error:
        return f"❌ Error: {error}"

@mcp.tool()
def send_email(to: str, subject: str, body: str):
    """Send a simple email via Gmail."""
    try:
        service = get_gmail_service()
        message = EmailMessage()
        message.set_content(body)
        message['To'], message['Subject'] = to, subject
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = service.users().messages().send(userId="me", body={'raw': encoded_message}).execute()
        return f"✅ Email sent! ID: {send_message['id']}"
    except HttpError as error:
        return f"❌ Error: {error}"

@mcp.tool()
def clean_spam():
    """Delete all messages in the Spam folder."""
    try:
        service = get_gmail_service()
        results = service.users().messages().list(userId='me', labelIds=['SPAM']).execute()
        messages = results.get('messages', [])
        if not messages: return "Spam folder is clean."
        for msg in messages: service.users().messages().delete(userId='me', id=msg['id']).execute()
        return f"✅ Cleaned {len(messages)} spam emails."
    except HttpError as error:
        return f"❌ Error: {error}"

@mcp.tool()
def search_drive(query: str):
    """Search for files in Google Drive."""
    try:
        service = get_drive_service()
        results = service.files().list(q=query, fields='files(id, name, mimeType)').execute()
        items = results.get('files', [])
        if not items: return "No files found."
        return "\n".join([f"- {item['name']} ({item['id']})" for item in items])
    except HttpError as error:
        return f"❌ Error: {error}"

if __name__ == "__main__":
    mcp.run()
