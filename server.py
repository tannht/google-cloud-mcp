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

# If modifying these scopes, delete the file token.json.
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

# Path configuration from env
CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
TOKEN_PATH = os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

mcp = FastMCP("Google Cloud MCP")

def get_credentials():
    creds = None
    # 1. Try loading from existing token file
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    # 2. If no valid credentials, run auth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Prefer Environment Variables over JSON file
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
                if not os.path.exists(CREDENTIALS_PATH):
                    raise FileNotFoundError(f"Missing Google Credentials. Set GOOGLE_CLIENT_ID/SECRET or provide {CREDENTIALS_PATH}")
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            
            creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
    return creds

def get_gmail_service():
    creds = get_credentials()
    return build('gmail', 'v1', credentials=creds)

def get_drive_service():
    creds = get_credentials()
    return build('drive', 'v3', credentials=creds)

# --- GMAIL TOOLS ---

@mcp.tool()
def create_gmail_label(name: str):
    """Create a new label in Gmail."""
    try:
        service = get_gmail_service()
        label = {'name': name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
        created_label = service.users().labels().create(userId='me', body=label).execute()
        return f"✅ Label '{name}' created successfully (ID: {created_label['id']})"
    except HttpError as error:
        return f"❌ Error creating label: {error}"

@mcp.tool()
def list_gmail_labels():
    """List all user labels in Gmail."""
    try:
        service = get_gmail_service()
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        if not labels:
            return "No labels found."
        user_labels = [l['name'] for l in labels if l['type'] == 'user']
        return "\n".join(user_labels)
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
        
        if not label_id:
            return f"❌ Error: Label '{label_name}' not found. Please create it first."
        
        add_labels = [label_id]
        remove_labels = []
        if archive:
            remove_labels.append('INBOX')
            
        filter_body = {
            'criteria': {'from': from_email},
            'action': {'addLabelIds': add_labels, 'removeLabelIds': remove_labels}
        }
        
        result = service.users().settings().filters().create(userId='me', body=filter_body).execute()
        return f"✅ Filter created for '{from_email}' (ID: {result['id']})"
    except HttpError as error:
        return f"❌ Error creating filter: {error}"

@mcp.tool()
def batch_label_emails(query: str, label_name: str):
    """Search for emails and apply a label to all matching messages."""
    try:
        service = get_gmail_service()
        labels_results = service.users().labels().list(userId='me').execute()
        labels = labels_results.get('labels', [])
        label_id = next((l['id'] for l in labels if l['name'] == label_name), None)
        
        if not label_id:
            return f"❌ Error: Label '{label_name}' not found."
        
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        
        if not messages:
            return f"No emails found matching query '{query}'."
        
        count = 0
        for msg in messages:
            service.users().messages().batchModify(userId='me', body={
                'ids': [msg['id']],
                'addLabelIds': [label_id]
            }).execute()
            count += 1
            
        return f"✅ Successfully labeled {count} emails as '{label_name}'."
    except HttpError as error:
        return f"❌ Error: {error}"

@mcp.tool()
def send_email(to: str, subject: str, body: str):
    """Send a simple email via Gmail."""
    try:
        service = get_gmail_service()
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to
        message['From'] = 'me'
        message['Subject'] = subject
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        return f"✅ Email sent! ID: {send_message['id']}"
    except HttpError as error:
        return f"❌ Error sending email: {error}"

@mcp.tool()
def clean_spam():
    """Delete all messages in the Spam folder."""
    try:
        service = get_gmail_service()
        results = service.users().messages().list(userId='me', labelIds=['SPAM']).execute()
        messages = results.get('messages', [])
        if not messages:
            return "Spam folder is already clean."
        
        count = 0
        for msg in messages:
            service.users().messages().delete(userId='me', id=msg['id']).execute()
            count += 1
        return f"✅ Cleaned {count} spam emails."
    except HttpError as error:
        return f"❌ Error cleaning spam: {error}"

# --- DRIVE TOOLS ---

@mcp.tool()
def search_drive(query: str):
    """Search for files in Google Drive."""
    try:
        service = get_drive_service()
        results = service.files().list(q=query, spaces='drive', fields='files(id, name, mimeType)').execute()
        items = results.get('files', [])
        if not items:
            return "No files found."
        output = [f"- {item['name']} ({item['id']})" for item in items]
        return "\n".join(output)
    except HttpError as error:
        return f"❌ Error: {error}"

if __name__ == "__main__":
    mcp.run()
