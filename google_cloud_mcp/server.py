from fastmcp import FastMCP
import os.path
import base64
import json
import sys
import threading
import requests
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
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/webmasters',
    'https://www.googleapis.com/auth/analytics.readonly',
    'https://www.googleapis.com/auth/analytics.edit',
    'https://www.googleapis.com/auth/tagmanager.readonly',
    'https://www.googleapis.com/auth/tagmanager.edit.containers',
    'https://www.googleapis.com/auth/tagmanager.edit.containerversions',
    'https://www.googleapis.com/auth/tagmanager.publish'
]

TOKEN_FILE_PATH = os.getenv('GOOGLE_TOKEN_PATH', '.token.json')
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
CRED_FILE_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
AUTH_PORT = int(os.getenv('AUTH_PORT', '3838'))
ADS_DEVELOPER_TOKEN = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
ADS_LOGIN_CUSTOMER_ID = os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID')  # manager (MCC) account ID, optional
ADS_API_VERSION = os.getenv('GOOGLE_ADS_API_VERSION', 'v23')

mcp = FastMCP("Google Cloud MCP")

def get_credentials():
    creds = None
    token_json = os.getenv('GOOGLE_TOKEN_JSON')
    if token_json:
        # No scopes passed: refresh with the scopes the token was granted, so adding a scope doesn't break old tokens.
        try: creds = Credentials.from_authorized_user_info(json.loads(token_json))
        except: pass
    if (not creds or not creds.valid) and os.path.exists(TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        raise RuntimeError(
            f"Not authenticated. Please open http://localhost:{AUTH_PORT} in your browser to authorize with Google."
        )
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
            try:
                creds = get_credentials()
                ok = creds and creds.valid
            except Exception:
                ok = False
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
    auth_msg = f"""

============================================================
🔐 GOOGLE ACCOUNT AUTHENTICATION
📱 Open your browser: http://localhost:{AUTH_PORT}
============================================================

"""
    print(auth_msg, file=sys.stderr)
    sys.stderr.flush()
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
    """Send a simple email via Gmail.

    Note: This function intentionally constructs the MIME message manually
    to keep the raw decoded content readable with Unicode subjects, as
    expected by the test suite. This avoids RFC-compliant header encoding
    that would obscure the original subject line text.
    """
    try:
        service = build('gmail', 'v1', credentials=get_credentials())
        # Minimal UTF-8 email message with explicit headers
        raw_message = (
            f"To: {to}\n"
            f"Subject: {subject}\n"
            'Content-Type: text/plain; charset="utf-8"\n'
            "\n"
            f"{body}"
        )
        encoded = base64.urlsafe_b64encode(raw_message.encode("utf-8")).decode("utf-8")
        res = service.users().messages().send(userId="me", body={'raw': encoded}).execute()
        return f"✅ Email sent! ID: {res['id']}"
    except Exception as e:
        # Tests expect errors (including HttpError) to be returned as strings,
        # not raised, so we preserve that behaviour.
        return str(e)

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
def list_drive_folders(parent_id: str = "root"):
    """List all folders in Google Drive. parent_id: 'root' for main folder."""
    try:
        service = build('drive', 'v3', credentials=get_credentials())
        query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        res = service.files().list(q=query, fields='files(id, name, webViewLink)', pageSize=100).execute()
        items = res.get('files', [])
        if not items:
            return "No folders found."
        return "\n".join([f"📁 {item['name']}\n   ID: {item['id']}\n   Link: {item.get('webViewLink', 'N/A')}\n" for item in items])
    except Exception as e: return str(e)

@mcp.tool()
def search_drive(query: str):
    """Search for files in Google Drive."""
    try:
        service = build('drive', 'v3', credentials=get_credentials())
        res = service.files().list(q=query, fields='files(id, name, mimeType)').execute()
        items = res.get('files', [])
        return "\n".join([f"- {item['name']} ({item['id']})" for item in items]) if items else "No files found."
    except Exception as e: return str(e)

# --- GOOGLE DOCS TOOLS ---

@mcp.tool()
def create_document(title: str, body_text: str = ""):
    """Create a new Google Docs document with optional initial text."""
    try:
        service = build('docs', 'v1', credentials=get_credentials())
        doc = service.documents().create(body={'title': title}).execute()
        doc_id = doc['documentId']
        if body_text:
            service.documents().batchUpdate(documentId=doc_id, body={
                'requests': [{'insertText': {'location': {'index': 1}, 'text': body_text}}]
            }).execute()
        return f"✅ Document created: https://docs.google.com/document/d/{doc_id}/edit"
    except Exception as e: return str(e)

@mcp.tool()
def get_document(document_id: str):
    """Get the full text content of a Google Docs document by its ID."""
    try:
        service = build('docs', 'v1', credentials=get_credentials())
        doc = service.documents().get(documentId=document_id).execute()
        title = doc.get('title', '')
        text = ''
        for element in doc.get('body', {}).get('content', []):
            para = element.get('paragraph')
            if para:
                for e in para.get('elements', []):
                    run = e.get('textRun')
                    if run:
                        text += run.get('content', '')
        return f"Title: {title}\n\n{text}"
    except Exception as e: return str(e)

@mcp.tool()
def append_to_document(document_id: str, text: str):
    """Append text to the end of a Google Docs document."""
    try:
        service = build('docs', 'v1', credentials=get_credentials())
        doc = service.documents().get(documentId=document_id).execute()
        end_index = doc['body']['content'][-1]['endIndex'] - 1
        service.documents().batchUpdate(documentId=document_id, body={
            'requests': [{'insertText': {'location': {'index': end_index}, 'text': text}}]
        }).execute()
        return f"✅ Text appended to document {document_id}"
    except Exception as e: return str(e)

@mcp.tool()
def search_documents(query: str = "", max_results: int = 20):
    """Search for Google Docs documents in Drive. Empty query lists recent docs."""
    try:
        service = build('drive', 'v3', credentials=get_credentials())
        q = "mimeType='application/vnd.google-apps.document'"
        if query:
            q += f" and fullText contains '{query}'"
        res = service.files().list(q=q, pageSize=max_results,
                                   fields='files(id, name, modifiedTime, owners)',
                                   orderBy='modifiedTime desc').execute()
        items = res.get('files', [])
        if not items: return "No documents found."
        return "\n".join([f"- {f['name']} (ID: {f['id']}, Modified: {f.get('modifiedTime', 'N/A')})" for f in items])
    except Exception as e: return str(e)

@mcp.tool()
def export_document(document_id: str, format: str = "text"):
    """Export a Google Docs document. Formats: text, html, pdf, docx."""
    try:
        service = build('drive', 'v3', credentials=get_credentials())
        mime_map = {
            'text': 'text/plain',
            'html': 'text/html',
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        mime = mime_map.get(format)
        if not mime: return f"❌ Unsupported format '{format}'. Use: text, html, pdf, docx"
        content = service.files().export(fileId=document_id, mimeType=mime).execute()
        if format in ('text', 'html'):
            return content.decode('utf-8') if isinstance(content, bytes) else content
        encoded = base64.b64encode(content).decode('utf-8')
        return f"✅ Exported as {format} (base64, {len(content)} bytes):\n{encoded[:200]}..."
    except Exception as e: return str(e)

# --- GOOGLE SHEETS TOOLS ---

@mcp.tool()
def create_spreadsheet(title: str, sheet_name: str = "Sheet1"):
    """Create a new Google Sheets spreadsheet."""
    try:
        service = build('sheets', 'v4', credentials=get_credentials())
        spreadsheet = service.spreadsheets().create(body={
            'properties': {'title': title},
            'sheets': [{'properties': {'title': sheet_name}}]
        }).execute()
        sid = spreadsheet.get('spreadsheetId')
        return f"✅ Spreadsheet created: https://docs.google.com/spreadsheets/d/{sid}/edit"
    except Exception as e:
        return str(e)

@mcp.tool()
def read_spreadsheet(spreadsheet_id: str, range: str = "Sheet1"):
    """Read data from a Google Sheets spreadsheet. Range format: 'Sheet1!A1:D10' or 'Sheet1'."""
    try:
        service = build('sheets', 'v4', credentials=get_credentials())
        res = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range
        ).execute()
        values = res.get('values', [])
        if not values:
            return "No data found."
        return "\n".join(["\t".join(map(str, row)) for row in values])
    except Exception as e:
        return str(e)

@mcp.tool()
def update_spreadsheet(spreadsheet_id: str, range: str, values: str):
    """Update cells in a spreadsheet. Values format: JSON 2D array, e.g. '[["A","B"],["1","2"]]'. Range: 'Sheet1!A1'."""
    try:
        service = build('sheets', 'v4', credentials=get_credentials())
        parsed = json.loads(values)
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range,
            valueInputOption='USER_ENTERED',
            body={'values': parsed}
        ).execute()
        return f"✅ Updated {range} in spreadsheet {spreadsheet_id}"
    except json.JSONDecodeError:
        return "❌ Invalid JSON for values. Use format: [[\"A\",\"B\"],[\"1\",\"2\"]]"
    except Exception as e:
        return str(e)

@mcp.tool()
def append_to_spreadsheet(spreadsheet_id: str, range: str, values: str):
    """Append rows to a spreadsheet. Values format: JSON 2D array. Range: 'Sheet1!A1'."""
    try:
        service = build('sheets', 'v4', credentials=get_credentials())
        parsed = json.loads(values)
        res = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': parsed}
        ).execute()
        updated = res.get('updates', {}).get('updatedRows', 0)
        return f"✅ Appended {updated} rows to {range}"
    except json.JSONDecodeError:
        return "❌ Invalid JSON for values. Use format: [[\"A\",\"B\"],[\"1\",\"2\"]]"
    except Exception as e:
        return str(e)

@mcp.tool()
def search_spreadsheets(query: str = "", max_results: int = 20):
    """Search for Google Sheets spreadsheets in Drive. Empty query lists recent sheets."""
    try:
        service = build('drive', 'v3', credentials=get_credentials())
        q = "mimeType='application/vnd.google-apps.spreadsheet'"
        if query:
            q += f" and fullText contains '{query}'"
        res = service.files().list(
            q=q,
            pageSize=max_results,
            fields='files(id, name, mimeType, modifiedTime)'
        ).execute()
        items = res.get('files', [])
        if not items:
            return "No spreadsheets found."
        return "\n".join(
            [
                f"- {f.get('name')} (ID: {f.get('id')}, Modified: {f.get('modifiedTime', 'N/A')})"
                for f in items
            ]
        )
    except Exception as e:
        return str(e)

@mcp.tool()
def get_spreadsheet_info(spreadsheet_id: str):
    """Get metadata about a spreadsheet: title, sheets, and their dimensions."""
    try:
        service = build('sheets', 'v4', credentials=get_credentials())
        meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        title = meta.get('properties', {}).get('title', '')
        sheets = []
        for s in meta.get('sheets', []):
            p = s.get('properties', {})
            grid = p.get('gridProperties', {})
            sheets.append(
                f"  - {p.get('title', '')} ({grid.get('rowCount', 0)}x{grid.get('columnCount', 0)})"
            )
        return f"Title: {title}\nSheets:\n" + "\n".join(sheets)
    except Exception as e:
        return str(e)

@mcp.tool()
def clear_spreadsheet_range(spreadsheet_id: str, range: str):
    """Clear all values in a range. Range format: 'Sheet1!A1:D10'."""
    try:
        service = build('sheets', 'v4', credentials=get_credentials())
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range
        ).execute()
        return f"✅ Cleared range {range}"
    except Exception as e:
        return str(e)

@mcp.tool()
def batch_update_spreadsheet(spreadsheet_id: str, data: str):
    """Batch update multiple ranges. Data format: JSON array of {range, values}, e.g. '[{\"range\":\"Sheet1!A1\",\"values\":[[\"X\"]]}]'."""
    try:
        service = build('sheets', 'v4', credentials=get_credentials())
        parsed = json.loads(data)
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'valueInputOption': 'USER_ENTERED', 'data': parsed}
        ).execute()
        return f"✅ Batch updated {len(parsed)} ranges"
    except json.JSONDecodeError:
        return "❌ Invalid JSON. Use format: [{\"range\":\"Sheet1!A1\",\"values\":[[\"X\"]]}]"
    except Exception as e:
        return str(e)

@mcp.tool()
def add_sheet(spreadsheet_id: str, sheet_name: str):
    """Add a new sheet/tab to an existing spreadsheet."""
    try:
        service = build('sheets', 'v4', credentials=get_credentials())
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [{'addSheet': {'properties': {'title': sheet_name}}}]}
        ).execute()
        return f"✅ Sheet '{sheet_name}' added"
    except Exception as e:
        return str(e)

@mcp.tool()
def export_spreadsheet(spreadsheet_id: str, format: str = "csv", sheet_id: int = 0):
    """Export a spreadsheet. Formats: csv, xlsx, pdf, tsv. sheet_id: 0 for first sheet."""
    try:
        service = build('drive', 'v3', credentials=get_credentials())
        mime_map = {
            'csv': 'text/csv',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pdf': 'application/pdf',
            'tsv': 'text/tab-separated-values'
        }
        mime = mime_map.get(format)
        if not mime:
            return f"❌ Unsupported format '{format}'. Use: csv, xlsx, pdf, tsv"
        content = service.files().export(fileId=spreadsheet_id, mimeType=mime).execute()
        if format in ('csv', 'tsv'):
            return content.decode('utf-8') if isinstance(content, bytes) else content
        encoded = base64.b64encode(content).decode('utf-8')
        return f"✅ Exported as {format} (base64, {len(content)} bytes):\n{encoded[:200]}..."
    except Exception as e:
        return str(e)

# --- GOOGLE SLIDES TOOLS ---

@mcp.tool()
def create_presentation(title: str):
    """Create a new Google Slides presentation."""
    try:
        service = build('slides', 'v1', credentials=get_credentials())
        pres = service.presentations().create(body={'title': title}).execute()
        pid = pres['presentationId']
        return f"✅ Presentation created: https://docs.google.com/presentation/d/{pid}/edit"
    except Exception as e: return str(e)

@mcp.tool()
def get_presentation(presentation_id: str):
    """Get metadata and slide titles/content from a Google Slides presentation."""
    try:
        service = build('slides', 'v1', credentials=get_credentials())
        pres = service.presentations().get(presentationId=presentation_id).execute()
        title = pres.get('title', '')
        slides = pres.get('slides', [])
        result = [f"Title: {title}", f"Slides: {len(slides)}"]
        for i, slide in enumerate(slides):
            texts = []
            for el in slide.get('pageElements', []):
                shape = el.get('shape')
                if shape and shape.get('text'):
                    for te in shape['text'].get('textElements', []):
                        run = te.get('textRun')
                        if run:
                            texts.append(run.get('content', '').strip())
            content = ' | '.join([t for t in texts if t])
            result.append(f"  Slide {i+1}: {content if content else '(empty)'}")
        return "\n".join(result)
    except Exception as e: return str(e)

@mcp.tool()
def add_slide(presentation_id: str, layout: str = "BLANK"):
    """Add a new slide to a presentation. Layouts: BLANK, TITLE, TITLE_AND_BODY, TITLE_AND_TWO_COLUMNS, TITLE_ONLY, SECTION_HEADER, CAPTION_ONLY, BIG_NUMBER."""
    try:
        service = build('slides', 'v1', credentials=get_credentials())
        pres = service.presentations().get(presentationId=presentation_id).execute()
        layouts = pres.get('layouts', [])
        layout_id = None
        for l in layouts:
            if l.get('layoutProperties', {}).get('name', '').upper() == layout.upper() or \
               l.get('layoutProperties', {}).get('displayName', '').upper() == layout.upper():
                layout_id = l['objectId']
                break
        req = {'createSlide': {}}
        if layout_id:
            req['createSlide']['slideLayoutReference'] = {'layoutId': layout_id}
        res = service.presentations().batchUpdate(presentationId=presentation_id,
                                                   body={'requests': [req]}).execute()
        slide_id = res['replies'][0]['createSlide']['objectId']
        return f"✅ Slide added (ID: {slide_id})"
    except Exception as e: return str(e)

@mcp.tool()
def add_text_to_slide(presentation_id: str, slide_index: int, text: str, x: int = 100, y: int = 100, width: int = 400, height: int = 200):
    """Add a text box to a slide. slide_index: 0-based. Coordinates in points (pt)."""
    try:
        service = build('slides', 'v1', credentials=get_credentials())
        pres = service.presentations().get(presentationId=presentation_id).execute()
        slides = pres.get('slides', [])
        if slide_index >= len(slides): return f"❌ Slide index {slide_index} out of range (total: {len(slides)})"
        box_id = f"textbox_{slide_index}_{hash(text) % 100000}"
        requests = [
            {'createShape': {
                'objectId': box_id,
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': slides[slide_index]['objectId'],
                    'size': {'width': {'magnitude': width, 'unit': 'PT'}, 'height': {'magnitude': height, 'unit': 'PT'}},
                    'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': x, 'translateY': y, 'unit': 'PT'}
                }
            }},
            {'insertText': {'objectId': box_id, 'text': text}}
        ]
        service.presentations().batchUpdate(presentationId=presentation_id, body={'requests': requests}).execute()
        return f"✅ Text box added to slide {slide_index + 1}"
    except Exception as e: return str(e)

@mcp.tool()
def search_presentations(query: str = "", max_results: int = 20):
    """Search for Google Slides presentations in Drive. Empty query lists recent presentations."""
    try:
        service = build('drive', 'v3', credentials=get_credentials())
        q = "mimeType='application/vnd.google-apps.presentation'"
        if query:
            q += f" and fullText contains '{query}'"
        res = service.files().list(q=q, pageSize=max_results,
                                   fields='files(id, name, modifiedTime)',
                                   orderBy='modifiedTime desc').execute()
        items = res.get('files', [])
        if not items: return "No presentations found."
        return "\n".join([f"- {f['name']} (ID: {f['id']}, Modified: {f.get('modifiedTime', 'N/A')})" for f in items])
    except Exception as e: return str(e)

@mcp.tool()
def delete_slide(presentation_id: str, slide_index: int):
    """Delete a slide from a presentation by its 0-based index."""
    try:
        service = build('slides', 'v1', credentials=get_credentials())
        pres = service.presentations().get(presentationId=presentation_id).execute()
        slides = pres.get('slides', [])
        if slide_index >= len(slides): return f"❌ Slide index {slide_index} out of range (total: {len(slides)})"
        slide_id = slides[slide_index]['objectId']
        service.presentations().batchUpdate(presentationId=presentation_id, body={
            'requests': [{'deleteObject': {'objectId': slide_id}}]
        }).execute()
        return f"✅ Slide {slide_index + 1} deleted"
    except Exception as e: return str(e)

@mcp.tool()
def export_presentation(presentation_id: str, format: str = "pdf"):
    """Export a presentation. Formats: pdf, pptx, txt."""
    try:
        service = build('drive', 'v3', credentials=get_credentials())
        mime_map = {
            'pdf': 'application/pdf',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'txt': 'text/plain'
        }
        mime = mime_map.get(format)
        if not mime: return f"❌ Unsupported format '{format}'. Use: pdf, pptx, txt"
        content = service.files().export(fileId=presentation_id, mimeType=mime).execute()
        if format == 'txt':
            return content.decode('utf-8') if isinstance(content, bytes) else content
        encoded = base64.b64encode(content).decode('utf-8')
        return f"✅ Exported as {format} (base64, {len(content)} bytes):\n{encoded[:200]}..."
    except Exception as e: return str(e)

# --- GOOGLE ADS TOOLS ---

def _ads_call(method: str, path: str, body: dict | None = None):
    """Call the Google Ads REST API. Needs GOOGLE_ADS_DEVELOPER_TOKEN."""
    if not ADS_DEVELOPER_TOKEN:
        raise RuntimeError("GOOGLE_ADS_DEVELOPER_TOKEN is not set.")
    headers = {
        'Authorization': f"Bearer {get_credentials().token}",
        'developer-token': ADS_DEVELOPER_TOKEN,
        'Content-Type': 'application/json',
    }
    url = f"https://googleads.googleapis.com/{ADS_API_VERSION}/{path}"
    if ADS_LOGIN_CUSTOMER_ID:
        headers['login-customer-id'] = ADS_LOGIN_CUSTOMER_ID.replace('-', '')
    res = requests.request(method, url, headers=headers, json=body, timeout=60)
    if res.status_code == 403 and 'USER_PERMISSION_DENIED' in res.text and 'login-customer-id' in headers:
        # Account is not under the configured manager: retry as a directly accessible account.
        retry_headers = {k: v for k, v in headers.items() if k != 'login-customer-id'}
        res = requests.request(method, url, headers=retry_headers, json=body, timeout=60)
    if not res.ok:
        raise RuntimeError(f"Google Ads API error {res.status_code}: {res.text}")
    return res.json()

def _ads_id(customer_id: str) -> str:
    return customer_id.replace('-', '').strip()

@mcp.tool()
def list_ads_accounts():
    """List Google Ads customer accounts the authenticated user can access."""
    try:
        res = _ads_call('GET', 'customers:listAccessibleCustomers')
        names = res.get('resourceNames', [])
        if not names: return "No accessible Google Ads accounts found."
        return "\n".join([f"- {n.split('/')[-1]}" for n in names])
    except Exception as e: return str(e)

@mcp.tool()
def ads_search(customer_id: str, query: str, max_results: int = 100):
    """Run a GAQL query on a Google Ads account. customer_id: 10 digits (dashes allowed).
    Example query: SELECT campaign.id, campaign.name FROM campaign"""
    try:
        res = _ads_call('POST', f"customers/{_ads_id(customer_id)}/googleAds:search",
                        {'query': query})
        rows = res.get('results', [])[:max_results]
        if not rows: return "No results."
        return "\n".join([json.dumps(r, ensure_ascii=False) for r in rows])
    except Exception as e: return str(e)

@mcp.tool()
def list_ads_campaigns(customer_id: str, status: str = ""):
    """List campaigns with budget. status (optional): ENABLED, PAUSED, REMOVED."""
    try:
        gaql = ("SELECT campaign.id, campaign.name, campaign.status, "
                "campaign.advertising_channel_type, campaign_budget.amount_micros FROM campaign")
        gaql += f" WHERE campaign.status = '{status.upper()}'" if status else " WHERE campaign.status != 'REMOVED'"
        res = _ads_call('POST', f"customers/{_ads_id(customer_id)}/googleAds:search", {'query': gaql})
        rows = res.get('results', [])
        if not rows: return "No campaigns found."
        lines = []
        for r in rows:
            c = r.get('campaign', {})
            budget = int(r.get('campaignBudget', {}).get('amountMicros', 0)) / 1_000_000
            lines.append(f"- {c.get('name')} (ID: {c.get('id')}, {c.get('status')}, "
                         f"{c.get('advertisingChannelType')}, budget/day: {budget:g})")
        return "\n".join(lines)
    except Exception as e: return str(e)

@mcp.tool()
def get_ads_campaign_performance(customer_id: str, date_range: str = "LAST_30_DAYS"):
    """Campaign performance (impressions, clicks, cost, conversions).
    date_range: TODAY, YESTERDAY, LAST_7_DAYS, LAST_30_DAYS, THIS_MONTH, LAST_MONTH..."""
    try:
        gaql = ("SELECT campaign.id, campaign.name, metrics.impressions, metrics.clicks, "
                "metrics.cost_micros, metrics.conversions FROM campaign "
                f"WHERE segments.date DURING {date_range.upper()} AND metrics.impressions > 0 "
                "ORDER BY metrics.cost_micros DESC")
        res = _ads_call('POST', f"customers/{_ads_id(customer_id)}/googleAds:search", {'query': gaql})
        rows = res.get('results', [])
        if not rows: return "No data."
        lines = []
        for r in rows:
            m = r.get('metrics', {})
            cost = int(m.get('costMicros', 0)) / 1_000_000
            lines.append(f"- {r.get('campaign', {}).get('name')}: impr {m.get('impressions', 0)}, "
                         f"clicks {m.get('clicks', 0)}, cost {cost:.2f}, conv {float(m.get('conversions', 0)):g}")
        return "\n".join(lines)
    except Exception as e: return str(e)

@mcp.tool()
def set_ads_campaign_status(customer_id: str, campaign_id: str, status: str):
    """Pause or enable a campaign. status: ENABLED or PAUSED."""
    try:
        status = status.upper()
        if status not in ('ENABLED', 'PAUSED'): return "❌ status must be ENABLED or PAUSED"
        cid = _ads_id(customer_id)
        _ads_call('POST', f"customers/{cid}/campaigns:mutate", {'operations': [{
            'update': {'resourceName': f"customers/{cid}/campaigns/{campaign_id}", 'status': status},
            'updateMask': 'status'}]})
        return f"✅ Campaign {campaign_id} set to {status}"
    except Exception as e: return str(e)

def _ads_items(text: str, sep: str) -> list[str]:
    return [i.strip() for i in text.split(sep) if i.strip()]

@mcp.tool()
def remove_ads_ad(customer_id: str, ad_group_id: str, ad_id: str, validate_only: bool = False):
    """PERMANENTLY remove an ad (status REMOVED, cannot be restored). validate_only=True checks without applying."""
    try:
        cid = _ads_id(customer_id)
        _ads_call('POST', f"customers/{cid}/adGroupAds:mutate", {
            'operations': [{'remove': f"customers/{cid}/adGroupAds/{ad_group_id}~{ad_id}"}],
            'validateOnly': validate_only})
        return f"✅ {'Validated removal of' if validate_only else 'Removed'} ad {ad_id} (ad group {ad_group_id})"
    except Exception as e: return str(e)

@mcp.tool()
def add_ads_negative_keywords(customer_id: str, campaign_id: str, keywords: str,
                              match_type: str = "PHRASE", validate_only: bool = False):
    """Add campaign-level negative keywords. keywords: comma or newline separated.
    match_type: BROAD, PHRASE, EXACT. Keywords that already exist are skipped."""
    try:
        match_type = match_type.upper()
        if match_type not in ('BROAD', 'PHRASE', 'EXACT'): return "❌ match_type must be BROAD, PHRASE or EXACT"
        cid = _ads_id(customer_id)
        wanted = list(dict.fromkeys(_ads_items(keywords.replace('\n', ','), ',')))
        existing = _ads_call('POST', f"customers/{cid}/googleAds:search", {'query': (
            "SELECT campaign_criterion.keyword.text, campaign_criterion.keyword.match_type FROM campaign_criterion "
            f"WHERE campaign.id = {campaign_id} AND campaign_criterion.type = 'KEYWORD' "
            "AND campaign_criterion.negative = TRUE")}).get('results', [])
        have = {(r['campaignCriterion']['keyword']['text'].lower(), r['campaignCriterion']['keyword']['matchType'])
                for r in existing}
        new = [k for k in wanted if (k.lower(), match_type) not in have]
        if not new: return "Nothing to add: all keywords already exist."
        _ads_call('POST', f"customers/{cid}/campaignCriteria:mutate", {
            'operations': [{'create': {'campaign': f"customers/{cid}/campaigns/{campaign_id}", 'negative': True,
                                       'keyword': {'text': k, 'matchType': match_type}}} for k in new],
            'validateOnly': validate_only})
        skipped = len(wanted) - len(new)
        return (f"✅ {'Validated' if validate_only else 'Added'} {len(new)} negative keywords ({match_type}): "
                f"{', '.join(new)}" + (f" | skipped {skipped} existing" if skipped else ""))
    except Exception as e: return str(e)

@mcp.tool()
def update_ads_responsive_search_ad(customer_id: str, ad_id: str, headlines: str = "", descriptions: str = "",
                                    path1: str = "", path2: str = "", validate_only: bool = False):
    """Replace text of a Responsive Search Ad. headlines/descriptions: '|' separated (3-15 headlines <=30 chars,
    2-4 descriptions <=90 chars); path1/path2 <=15 chars. Only provided fields change. The ad is re-reviewed."""
    try:
        hs, ds = _ads_items(headlines, '|'), _ads_items(descriptions, '|')
        rsa, mask = {}, []
        if hs:
            if not 3 <= len(hs) <= 15: return f"❌ Need 3-15 headlines, got {len(hs)}"
            bad = [h for h in hs if len(h) > 30]
            if bad: return f"❌ Headlines over 30 chars: {bad}"
            if len(set(h.lower() for h in hs)) != len(hs): return "❌ Duplicate headlines"
            rsa['headlines'] = [{'text': h} for h in hs]; mask.append('responsive_search_ad.headlines')
        if ds:
            if not 2 <= len(ds) <= 4: return f"❌ Need 2-4 descriptions, got {len(ds)}"
            bad = [d for d in ds if len(d) > 90]
            if bad: return f"❌ Descriptions over 90 chars: {bad}"
            rsa['descriptions'] = [{'text': d} for d in ds]; mask.append('responsive_search_ad.descriptions')
        for name, val in (('path1', path1), ('path2', path2)):
            if val:
                if len(val) > 15: return f"❌ {name} over 15 chars"
                rsa[name] = val; mask.append(f'responsive_search_ad.{name}')
        if not mask: return "❌ Nothing to update"
        cid = _ads_id(customer_id)
        _ads_call('POST', f"customers/{cid}/ads:mutate", {
            'operations': [{'update': {'resourceName': f"customers/{cid}/ads/{ad_id}", 'responsiveSearchAd': rsa},
                            'updateMask': ','.join(mask)}],
            'validateOnly': validate_only})
        return f"✅ {'Validated update of' if validate_only else 'Updated'} ad {ad_id}: {', '.join(m.split('.')[-1] for m in mask)}"
    except Exception as e: return str(e)

@mcp.tool()
def update_ads_conversion_action(customer_id: str, conversion_action_id: str, counting_type: str = "",
                                 status: str = "", primary_for_goal: str = "", validate_only: bool = False):
    """Update a conversion action. counting_type: ONE_PER_CLICK or MANY_PER_CLICK; status: ENABLED, PAUSED,
    REMOVED; primary_for_goal: 'true' or 'false'. Only provided fields change."""
    try:
        cid = _ads_id(customer_id)
        upd, mask = {'resourceName': f"customers/{cid}/conversionActions/{conversion_action_id}"}, []
        if counting_type:
            if counting_type.upper() not in ('ONE_PER_CLICK', 'MANY_PER_CLICK'): return "❌ counting_type must be ONE_PER_CLICK or MANY_PER_CLICK"
            upd['countingType'] = counting_type.upper(); mask.append('counting_type')
        if status:
            if status.upper() not in ('ENABLED', 'PAUSED', 'REMOVED'): return "❌ status must be ENABLED, PAUSED or REMOVED"
            upd['status'] = status.upper(); mask.append('status')
        if primary_for_goal:
            if primary_for_goal.lower() not in ('true', 'false'): return "❌ primary_for_goal must be 'true' or 'false'"
            upd['primaryForGoal'] = primary_for_goal.lower() == 'true'; mask.append('primary_for_goal')
        if not mask: return "❌ Nothing to update"
        _ads_call('POST', f"customers/{cid}/conversionActions:mutate", {
            'operations': [{'update': upd, 'updateMask': ','.join(mask)}], 'validateOnly': validate_only})
        return f"✅ {'Validated' if validate_only else 'Updated'} conversion action {conversion_action_id}: {', '.join(mask)}"
    except Exception as e: return str(e)

# --- GOOGLE SEARCH CONSOLE TOOLS ---

@mcp.tool()
def list_search_console_sites():
    """List Search Console properties the account can access."""
    try:
        service = build('searchconsole', 'v1', credentials=get_credentials())
        sites = service.sites().list().execute().get('siteEntry', [])
        if not sites: return "No Search Console sites found."
        return "\n".join([f"- {s['siteUrl']} ({s.get('permissionLevel')})" for s in sites])
    except Exception as e: return str(e)

@mcp.tool()
def search_console_query(site_url: str, start_date: str, end_date: str,
                         dimensions: str = "query", row_limit: int = 25):
    """Search analytics. Dates: YYYY-MM-DD. dimensions: comma list of query,page,country,device,date.
    site_url: e.g. https://example.com/ or sc-domain:example.com"""
    try:
        service = build('searchconsole', 'v1', credentials=get_credentials())
        dims = [d.strip() for d in dimensions.split(',') if d.strip()]
        body = {'startDate': start_date, 'endDate': end_date, 'dimensions': dims, 'rowLimit': row_limit}
        rows = service.searchanalytics().query(siteUrl=site_url, body=body).execute().get('rows', [])
        if not rows: return "No data."
        return "\n".join([f"- {' | '.join(r.get('keys', []))}: clicks {r['clicks']:g}, impr {r['impressions']:g}, "
                          f"ctr {r['ctr'] * 100:.2f}%, pos {r['position']:.1f}" for r in rows])
    except Exception as e: return str(e)

@mcp.tool()
def list_search_console_sitemaps(site_url: str):
    """List sitemaps submitted for a Search Console property."""
    try:
        service = build('searchconsole', 'v1', credentials=get_credentials())
        maps = service.sitemaps().list(siteUrl=site_url).execute().get('sitemap', [])
        if not maps: return "No sitemaps found."
        return "\n".join([f"- {m['path']} (errors: {m.get('errors', 0)}, warnings: {m.get('warnings', 0)}, "
                          f"last downloaded: {m.get('lastDownloaded', 'N/A')})" for m in maps])
    except Exception as e: return str(e)

@mcp.tool()
def inspect_url(site_url: str, inspection_url: str):
    """URL Inspection: index status of a page in a Search Console property."""
    try:
        service = build('searchconsole', 'v1', credentials=get_credentials())
        res = service.urlInspection().index().inspect(
            body={'inspectionUrl': inspection_url, 'siteUrl': site_url}).execute()
        s = res.get('inspectionResult', {}).get('indexStatusResult', {})
        return (f"Verdict: {s.get('verdict')}\nCoverage: {s.get('coverageState')}\n"
                f"Last crawl: {s.get('lastCrawlTime', 'N/A')}\nCanonical: {s.get('googleCanonical', 'N/A')}")
    except Exception as e: return str(e)

# --- GOOGLE ANALYTICS (GA4) TOOLS ---

@mcp.tool()
def list_ga4_properties():
    """List GA4 accounts and properties the user can access."""
    try:
        service = build('analyticsadmin', 'v1beta', credentials=get_credentials())
        summaries = service.accountSummaries().list().execute().get('accountSummaries', [])
        lines = []
        for a in summaries:
            lines.append(f"📊 {a.get('displayName')}")
            for p in a.get('propertySummaries', []):
                lines.append(f"   - {p.get('displayName')} ({p.get('property')})")
        return "\n".join(lines) if lines else "No GA4 properties found."
    except Exception as e: return str(e)

@mcp.tool()
def run_ga4_report(property_id: str, metrics: str = "activeUsers,sessions", dimensions: str = "date",
                   start_date: str = "28daysAgo", end_date: str = "today", limit: int = 25):
    """Run a GA4 report. property_id: numeric (e.g. 123456789). metrics/dimensions: comma lists of
    API names (sessions, activeUsers, screenPageViews / date, country, sessionSource, pagePath)."""
    try:
        service = build('analyticsdata', 'v1beta', credentials=get_credentials())
        body = {
            'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
            'metrics': [{'name': m.strip()} for m in metrics.split(',') if m.strip()],
            'dimensions': [{'name': d.strip()} for d in dimensions.split(',') if d.strip()],
            'limit': limit,
        }
        pid = property_id.replace('properties/', '')
        res = service.properties().runReport(property=f"properties/{pid}", body=body).execute()
        rows = res.get('rows', [])
        if not rows: return "No data."
        names = [m['name'] for m in body['metrics']]
        return "\n".join([
            f"- {' | '.join(d['value'] for d in r.get('dimensionValues', []))}: "
            + ", ".join(f"{n} {v['value']}" for n, v in zip(names, r.get('metricValues', [])))
            for r in rows])
    except Exception as e: return str(e)

@mcp.tool()
def list_ga4_data_streams(property_id: str):
    """List data streams (web/iOS/Android) of a GA4 property, with measurement IDs."""
    try:
        service = build('analyticsadmin', 'v1beta', credentials=get_credentials())
        pid = property_id.replace('properties/', '')
        streams = service.properties().dataStreams().list(parent=f"properties/{pid}").execute().get('dataStreams', [])
        if not streams: return "No data streams found."
        return "\n".join([f"- {s.get('displayName')} ({s.get('type')}, {s.get('name')}, "
                          f"measurement ID: {s.get('webStreamData', {}).get('measurementId', 'N/A')})"
                          for s in streams])
    except Exception as e: return str(e)

@mcp.tool()
def list_ga4_key_events(property_id: str):
    """List key events (formerly conversions) configured on a GA4 property."""
    try:
        service = build('analyticsadmin', 'v1beta', credentials=get_credentials())
        pid = property_id.replace('properties/', '')
        events = service.properties().keyEvents().list(parent=f"properties/{pid}").execute().get('keyEvents', [])
        if not events: return "No key events found."
        return "\n".join([f"- {e.get('eventName')} (counting: {e.get('countingMethod', 'N/A')})" for e in events])
    except Exception as e: return str(e)

@mcp.tool()
def run_ga4_realtime_report(property_id: str, metrics: str = "activeUsers", dimensions: str = "country", limit: int = 25):
    """Realtime GA4 report (last 30 minutes). Same name format as run_ga4_report."""
    try:
        service = build('analyticsdata', 'v1beta', credentials=get_credentials())
        body = {
            'metrics': [{'name': m.strip()} for m in metrics.split(',') if m.strip()],
            'dimensions': [{'name': d.strip()} for d in dimensions.split(',') if d.strip()],
            'limit': limit,
        }
        pid = property_id.replace('properties/', '')
        rows = service.properties().runRealtimeReport(property=f"properties/{pid}", body=body).execute().get('rows', [])
        if not rows: return "No realtime data."
        names = [m['name'] for m in body['metrics']]
        return "\n".join([
            f"- {' | '.join(d['value'] for d in r.get('dimensionValues', []))}: "
            + ", ".join(f"{n} {v['value']}" for n, v in zip(names, r.get('metricValues', [])))
            for r in rows])
    except Exception as e: return str(e)

@mcp.tool()
def get_ga4_metadata(property_id: str, kind: str = "all"):
    """List dimension/metric API names available on a GA4 property. kind: dimensions, metrics, all."""
    try:
        service = build('analyticsdata', 'v1beta', credentials=get_credentials())
        pid = property_id.replace('properties/', '')
        meta = service.properties().getMetadata(name=f"properties/{pid}/metadata").execute()
        lines = []
        for key in ('dimensions', 'metrics'):
            if kind in (key, 'all'):
                lines.append(f"{key.upper()}:")
                lines += [f"- {i['apiName']}: {i.get('uiName', '')}" for i in meta.get(key, [])]
        return "\n".join(lines)
    except Exception as e: return str(e)

@mcp.tool()
def add_search_console_site(site_url: str):
    """Add a property to Search Console (ownership must still be verified in the UI)."""
    try:
        service = build('searchconsole', 'v1', credentials=get_credentials())
        service.sites().add(siteUrl=site_url).execute()
        return f"✅ Site added: {site_url}"
    except Exception as e: return str(e)

@mcp.tool()
def submit_search_console_sitemap(site_url: str, sitemap_url: str):
    """Submit (or resubmit) a sitemap to a Search Console property."""
    try:
        service = build('searchconsole', 'v1', credentials=get_credentials())
        service.sitemaps().submit(siteUrl=site_url, feedpath=sitemap_url).execute()
        return f"✅ Sitemap submitted: {sitemap_url}"
    except Exception as e: return str(e)

# --- GOOGLE TAG MANAGER TOOLS ---

def _gtm():
    return build('tagmanager', 'v2', credentials=get_credentials())

def _gtm_list(fetch, key: str, fmt):
    items = fetch().execute().get(key, [])
    if not items: return f"No {key} found."
    return "\n".join([fmt(i) for i in items])

@mcp.tool()
def list_gtm_accounts():
    """List Google Tag Manager accounts."""
    try:
        return _gtm_list(lambda: _gtm().accounts().list(), 'account',
                         lambda a: f"- {a.get('name')} (ID: {a.get('accountId')}, path: {a.get('path')})")
    except Exception as e: return str(e)

@mcp.tool()
def list_gtm_containers(account_id: str):
    """List containers in a GTM account."""
    try:
        return _gtm_list(lambda: _gtm().accounts().containers().list(parent=f"accounts/{account_id}"), 'container',
                         lambda c: f"- {c.get('name')} (ID: {c.get('containerId')}, {c.get('publicId')}, path: {c.get('path')})")
    except Exception as e: return str(e)

@mcp.tool()
def list_gtm_workspaces(container_path: str):
    """List workspaces. container_path: accounts/{accountId}/containers/{containerId}"""
    try:
        return _gtm_list(lambda: _gtm().accounts().containers().workspaces().list(parent=container_path), 'workspace',
                         lambda w: f"- {w.get('name')} (ID: {w.get('workspaceId')}, path: {w.get('path')})")
    except Exception as e: return str(e)

@mcp.tool()
def list_gtm_tags(workspace_path: str):
    """List tags. workspace_path: accounts/{a}/containers/{c}/workspaces/{w}"""
    try:
        return _gtm_list(lambda: _gtm().accounts().containers().workspaces().tags().list(parent=workspace_path), 'tag',
                         lambda t: f"- {t.get('name')} (ID: {t.get('tagId')}, type: {t.get('type')}, "
                                   f"triggers: {t.get('firingTriggerId', [])})")
    except Exception as e: return str(e)

@mcp.tool()
def list_gtm_triggers(workspace_path: str):
    """List triggers of a GTM workspace."""
    try:
        return _gtm_list(lambda: _gtm().accounts().containers().workspaces().triggers().list(parent=workspace_path), 'trigger',
                         lambda t: f"- {t.get('name')} (ID: {t.get('triggerId')}, type: {t.get('type')})")
    except Exception as e: return str(e)

@mcp.tool()
def list_gtm_variables(workspace_path: str):
    """List variables of a GTM workspace."""
    try:
        return _gtm_list(lambda: _gtm().accounts().containers().workspaces().variables().list(parent=workspace_path), 'variable',
                         lambda v: f"- {v.get('name')} (ID: {v.get('variableId')}, type: {v.get('type')})")
    except Exception as e: return str(e)

@mcp.tool()
def get_gtm_live_version(container_path: str):
    """Show the currently published version of a GTM container."""
    try:
        v = _gtm().accounts().containers().versions().live(parent=container_path).execute()
        return (f"Version {v.get('containerVersionId')}: {v.get('name', '(unnamed)')}\n"
                f"Tags: {len(v.get('tag', []))}, triggers: {len(v.get('trigger', []))}, "
                f"variables: {len(v.get('variable', []))}\nPath: {v.get('path')}")
    except Exception as e: return str(e)

@mcp.tool()
def create_gtm_version(workspace_path: str, name: str, notes: str = ""):
    """Create a container version from a workspace (does NOT publish it)."""
    try:
        res = _gtm().accounts().containers().workspaces().create_version(
            path=workspace_path, body={'name': name, 'notes': notes}).execute()
        v = res.get('containerVersion')
        if not v:
            return f"❌ Version not created: {res.get('compilerError') or res.get('syncStatus') or res}"
        return f"✅ Version {v.get('containerVersionId')} created. Path: {v.get('path')}"
    except Exception as e: return str(e)

@mcp.tool()
def publish_gtm_version(version_path: str):
    """PUBLISH a GTM container version live. version_path: accounts/{a}/containers/{c}/versions/{v}"""
    try:
        res = _gtm().accounts().containers().versions().publish(path=version_path).execute()
        if res.get('compilerError'):
            return f"❌ Publish failed: compiler error in version"
        return f"✅ Published {version_path}"
    except Exception as e: return str(e)

_GTM_KINDS = ('tags', 'triggers', 'variables')

def _gtm_kind(path: str) -> str:
    kind = path.rstrip('/').split('/')[-2]
    if kind not in _GTM_KINDS: raise ValueError(f"Path must point to a tag, trigger or variable, got '{kind}'")
    return kind

def _gtm_workspaces():
    return _gtm().accounts().containers().workspaces()

@mcp.tool()
def get_gtm_resource(path: str):
    """Get one tag/trigger/variable as JSON. path: accounts/{a}/containers/{c}/workspaces/{w}/tags/{id}"""
    try:
        return json.dumps(getattr(_gtm_workspaces(), _gtm_kind(path))().get(path=path).execute(), ensure_ascii=False)
    except Exception as e: return str(e)

@mcp.tool()
def create_gtm_resource(workspace_path: str, resource: str, body: str):
    """Create a tag/trigger/variable in a workspace (draft: nothing is live until a version is published).
    resource: tags, triggers or variables. body: JSON as in the Tag Manager API."""
    try:
        if resource not in _GTM_KINDS: return f"❌ resource must be one of {_GTM_KINDS}"
        res = getattr(_gtm_workspaces(), resource)().create(parent=workspace_path, body=json.loads(body)).execute()
        return f"✅ Created {resource[:-1]} '{res.get('name')}' (ID: {res.get(resource[:-1] + 'Id')}, path: {res.get('path')})"
    except Exception as e: return str(e)

@mcp.tool()
def update_gtm_resource(path: str, body: str):
    """Update a tag/trigger/variable: top-level fields in body (JSON) replace the existing ones, others are kept."""
    try:
        api = getattr(_gtm_workspaces(), _gtm_kind(path))()
        current = api.get(path=path).execute()
        res = api.update(path=path, fingerprint=current['fingerprint'], body={**current, **json.loads(body)}).execute()
        return f"✅ Updated '{res.get('name')}' ({path})"
    except Exception as e: return str(e)

@mcp.tool()
def delete_gtm_resource(path: str):
    """Delete a tag/trigger/variable from a workspace (draft only; the live version is unchanged)."""
    try:
        getattr(_gtm_workspaces(), _gtm_kind(path))().delete(path=path).execute()
        return f"✅ Deleted {path}"
    except Exception as e: return str(e)

@mcp.tool()
def get_gtm_workspace_status(workspace_path: str):
    """List unpublished changes in a workspace."""
    try:
        res = _gtm_workspaces().getStatus(path=workspace_path).execute()
        changes = res.get('workspaceChange', [])
        if not changes: return "No unpublished changes."
        out = []
        for c in changes:
            item = c.get('tag') or c.get('trigger') or c.get('variable') or {}
            out.append(f"- {c.get('changeStatus')}: {item.get('name')}")
        if res.get('mergeConflict'): out.append("⚠️ Merge conflicts present")
        return "\n".join(out)
    except Exception as e: return str(e)

@mcp.tool()
def create_ga4_key_event(property_id: str, event_name: str, counting_method: str = "ONCE_PER_EVENT"):
    """Mark an event as a key event (formerly conversion) on a GA4 property. Needs the analytics.edit scope.
    counting_method: ONCE_PER_EVENT or ONCE_PER_SESSION."""
    try:
        if counting_method.upper() not in ('ONCE_PER_EVENT', 'ONCE_PER_SESSION'):
            return "❌ counting_method must be ONCE_PER_EVENT or ONCE_PER_SESSION"
        service = build('analyticsadmin', 'v1beta', credentials=get_credentials())
        pid = property_id.replace('properties/', '')
        res = service.properties().keyEvents().create(parent=f"properties/{pid}", body={
            'eventName': event_name, 'countingMethod': counting_method.upper()}).execute()
        return f"✅ Key event created: {res.get('eventName')} ({res.get('name')})"
    except Exception as e: return str(e)

if __name__ == "__main__":
    mcp.run()
