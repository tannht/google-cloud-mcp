from fastmcp import FastMCP
import os.path
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

# Path to credentials
CREDENTIALS_PATH = '/root/.openclaw/workspace/credentials/google_client_secret.json'
TOKEN_PATH = '/root/.google-mcp/tokens/my-google-account.json'

mcp = FastMCP("Google Cloud MCP")

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
    return build('gmail', 'v1', credentials=creds)

def get_drive_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
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
        return f"✅ Email sent successfully! Message ID: {send_message['id']}"
    except HttpError as error:
        return f"❌ Error sending email: {error}"

@mcp.tool()
def clean_spam():
    """Delete all messages in the Spam folder."""
    try:
        service = get_gmail_service()
        # Find messages in Spam
        results = service.users().messages().list(userId='me', labelIds=['SPAM']).execute()
        messages = results.get('messages', [])
        if not messages:
            return "Hòm thư Spam đã sạch bóng quân thù! Gâu!"
        
        for msg in messages:
            service.users().messages().delete(userId='me', id=msg['id']).execute()
        
        return f"✅ Đã dọn dẹp xong {len(messages)} thư rác. Sạch bong kin kít! 🐶🧹"
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
            return "No files found matching your query."
        output = []
        for item in items:
            output.append(f"- {item['name']} ({item['id']}) [{item['mimeType']}]")
        return "\n".join(output)
    except HttpError as error:
        return f"❌ Error searching drive: {error}"

if __name__ == "__main__":
    mcp.run()
