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

TOKEN_FILE_PATH = os.getenv('GOOGLE_TOKEN_PATH', '.token.json')
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
CRED_FILE_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')

mcp = FastMCP("Google Cloud MCP")

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

_pending_flow = None

class AuthPortalHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        global _pending_flow

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            creds = get_credentials()
            status_color = "#4CAF50" if (creds and creds.valid) else "#f44336"
            status_text = "✅ Authenticated" if (creds and creds.valid) else "❌ Not Authenticated"

            html = f"""
            <html>
            <head><title>PubPug Google Portal</title></head>
            <body style='font-family: sans-serif; padding: 50px; background: #f0f2f5; display: flex; justify-content: center;'>
                <div style='max-width: 500px; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center;'>
                    <h1 style='color: #1a73e8;'>🐶 PubPug Google MCP</h1>
                    <p style='font-size: 18px; color: {status_color}; font-weight: bold;'>{status_text}</p>
                    <hr style='border: 0; border-top: 1px solid #eee; margin: 20px 0;'>
                    <p style='color: #666;'>To empower your AI with Gmail, Drive, and more, please authorize below.</p>
                    <a href='/login' style='display: inline-block; padding: 15px 30px; background: #1a73e8; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 10px;'>🔑 Click to Authorize with Google</a>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))

        elif self.path == '/login':
            if CLIENT_ID and CLIENT_SECRET:
                config = {"installed": {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "redirect_uris": ["http://localhost:3838/callback"]}}
                _pending_flow = InstalledAppFlow.from_client_config(config, SCOPES, redirect_uri="http://localhost:3838/callback")
            else:
                _pending_flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE_PATH, SCOPES, redirect_uri="http://localhost:3838/callback")

            auth_url, _ = _pending_flow.authorization_url(prompt='consent', access_type='offline')
            self.send_response(302)
            self.send_header('Location', auth_url)
            self.end_headers()

        elif self.path.startswith('/callback'):
            from urllib.parse import urlparse, parse_qs
            try:
                params = parse_qs(urlparse(self.path).query)
                code = params.get('code', [None])[0]
                if not code:
                    raise ValueError("No authorization code received")
                if not _pending_flow:
                    raise ValueError("No pending auth flow. Please start from /login again.")

                _pending_flow.fetch_token(code=code)
                creds = _pending_flow.credentials

                with open(TOKEN_FILE_PATH, 'w') as f:
                    f.write(creds.to_json())
                print(f"✅ Token saved to {TOKEN_FILE_PATH}")

                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                html = """
                <html>
                <head><title>PubPug - Success</title></head>
                <body style='font-family: sans-serif; padding: 50px; background: #f0f2f5; display: flex; justify-content: center;'>
                    <div style='max-width: 500px; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center;'>
                        <h1 style='color: #4CAF50;'>✅ Authenticated!</h1>
                        <p style='color: #666;'>Token saved successfully. You can now use Google services through MCP.</p>
                        <a href='/' style='display: inline-block; padding: 10px 20px; background: #1a73e8; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px;'>Back to Portal</a>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(html.encode('utf-8'))
            except Exception as e:
                print(f"❌ Auth callback error: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                html = f"""
                <html>
                <head><title>PubPug - Error</title></head>
                <body style='font-family: sans-serif; padding: 50px; background: #f0f2f5; display: flex; justify-content: center;'>
                    <div style='max-width: 500px; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center;'>
                        <h1 style='color: #f44336;'>❌ Error</h1>
                        <p style='color: #666;'>{e}</p>
                        <a href='/login' style='display: inline-block; padding: 10px 20px; background: #1a73e8; color: white; text-decoration: none; border-radius: 5px; margin-top: 15px;'>Try Again</a>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(html.encode('utf-8'))

def start_portal():
    server = HTTPServer(('0.0.0.0', 3838), AuthPortalHandler)
    print("🌐 Auth Portal running at http://localhost:3838")
    server.serve_forever()

# Start portal in background
threading.Thread(target=start_portal, daemon=True).start()

# --- GMAIL TOOLS ---

def get_gmail_service():
    creds = get_credentials()
    if not creds: raise Exception("Not authenticated. Visit http://localhost:3838 to authorize.")
    return build('gmail', 'v1', credentials=creds)

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

if __name__ == "__main__":
    mcp.run()
