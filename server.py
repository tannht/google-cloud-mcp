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

class TokenDisplayHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        token_content = ""
        if os.path.exists(TOKEN_FILE_PATH):
            with open(TOKEN_FILE_PATH, 'r') as f:
                token_content = f.read()
        
        html = f"""
        <html>
        <head><title>PubPug Token Recovery</title></head>
        <body style='font-family: sans-serif; padding: 50px; line-height: 1.6; background: #f9f9f9;'>
            <div style='max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
                <h1 style='color: #4CAF50;'>🐶 PubPug: Auth Successful!</h1>
                <p>Authentication complete. Please copy the <b>Token JSON</b> below and use it for your <code>GOOGLE_TOKEN_JSON</code> environment variable.</p>
                <div style='margin: 20px 0;'>
                    <button onclick='copyToken()' style='padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;'>📋 Copy to Clipboard</button>
                </div>
                <textarea id='tokenArea' readonly style='width: 100%; height: 250px; padding: 15px; font-family: monospace; font-size: 12px; background: #222; color: #0f0; border-radius: 5px;'>{token_content}</textarea>
                <p style='margin-top: 20px; color: #666;'>You can now close this window and the server.</p>
            </div>
            <script>
                function copyToken() {{
                    var copyText = document.getElementById("tokenArea");
                    copyText.select();
                    copyText.setSelectionRange(0, 99999);
                    document.execCommand("copy");
                    alert("Token copied to clipboard! 🐶🦴");
                }}
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

def get_credentials():
    creds = None
    if TOKEN_JSON_ENV:
        try:
            creds = Credentials.from_authorized_user_info(json.loads(TOKEN_JSON_ENV), SCOPES)
            print("🐶 Using Token from environment variable.")
        except: pass

    if (not creds or not creds.valid) and os.path.exists(TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, SCOPES)
        print(f"🐶 Using Token from file: {TOKEN_FILE_PATH}")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Token expired. Refreshing...")
            creds.refresh(Request())
        else:
            print("🔑 No valid credentials. Starting OAuth flow...")
            if CLIENT_ID and CLIENT_SECRET:
                client_config = {"installed": {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "redirect_uris": ["http://localhost:3000"]}}
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE_PATH, SCOPES)
            
            creds = flow.run_local_server(port=3000, open_browser=False)
            
            with open(TOKEN_FILE_PATH, 'w') as token_file:
                token_file.write(creds.to_json())
            
            print("\n✅ Token saved. Displaying on http://localhost:3000 ...")
            # Briefly start a server to display the token on the same port
            # Note: In a real stdio MCP, this might be tricky, but for initial setup it works!
            
    return creds

def get_gmail_service():
    return build('gmail', 'v1', credentials=get_credentials())

def get_drive_service():
    return build('drive', 'v3', credentials=get_credentials())

# --- TOOLS ---

@mcp.tool()
def create_gmail_label(name: str):
    """Create a new label in Gmail."""
    try:
        service = get_gmail_service()
        label = {'name': name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
        res = service.users().labels().create(userId='me', body=label).execute()
        return f"✅ Label '{name}' created successfully (ID: {res['id']})"
    except HttpError as error: return f"❌ Error: {error}"

@mcp.tool()
def list_gmail_labels():
    """List all user labels in Gmail."""
    try:
        service = get_gmail_service()
        results = service.users().labels().list(userId='me').execute()
        labels = [l['name'] for l in results.get('labels', []) if l['type'] == 'user']
        return "\n".join(labels) if labels else "No user labels found."
    except HttpError as error: return f"❌ Error: {error}"

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
    except HttpError as error: return f"❌ Error: {error}"

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
    except HttpError as error: return f"❌ Error: {error}"

@mcp.tool()
def search_drive(query: str):
    """Search for files in Google Drive."""
    try:
        service = get_drive_service()
        results = service.files().list(q=query, fields='files(id, name, mimeType)').execute()
        items = results.get('files', [])
        if not items: return "No files found."
        return "\n".join([f"- {item['name']} ({item['id']})" for item in items])
    except HttpError as error: return f"❌ Error: {error}"

if __name__ == "__main__":
    mcp.run()
