# Google Cloud MCP - Google Workspace MCP Server (gg-mcp)

[![PyPI](https://img.shields.io/pypi/v/gg-mcp.svg)](https://pypi.org/project/gg-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Docker Support](https://img.shields.io/badge/Docker-Supported-blue.svg?logo=docker)](https://www.docker.com/)

A Model Context Protocol (MCP) server that connects AI agents to Google Workspace: **Gmail**, **Calendar**, **Drive**, **Docs**, **Sheets**, and **Slides**. Built with [FastMCP](https://github.com/jlowin/fastmcp).

```bash
# Install and run — that's it
uvx gg-mcp
```

---

## � Table of Contents
1. [Quick Start (5 minutes)](#-quick-start-5-minutes)
2. [Available Tools](#-available-tools-30)
3. [Installation Options](#-installation-options)
4. [Environment Variables](#-environment-variables)
5. [Troubleshooting](#-troubleshooting)
6. [Documentation](#-documentation)
7. [Development](#-development)

---

## 🚀 Quick Start (5 minutes)

### Step 1: Get Google OAuth Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable **OAuth consent screen** (External type)
3. Add required scopes (Gmail, Drive, Calendar, Docs, Sheets, Slides)
4. Create **OAuth 2.0 Desktop app** credentials
5. Copy **Client ID** and **Client Secret**

📖 **[Detailed guide →](GUIDE.md#step-1-get-your-google-oauth-credentials)**

### Step 2: Install & Run
```bash
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"
uvx gg-mcp
```

You'll see:
```
============================================================
🔐 GOOGLE ACCOUNT AUTHENTICATION
📱 Open your browser: http://localhost:3838
============================================================
```

Open `http://localhost:3838` → **"Authorize with Google"** → Grant permissions ✅

### Step 3: Configure MCP Client

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "gg-mcp": {
      "command": "uvx",
      "args": ["gg-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

Restart Claude Desktop and the tools are ready to use! 🎉

📖 **[25+ client configs →](MCP_CLIENTS.md)**

---

## 📋 Available Tools (30+)

### Account
- `get_account_info` - Get the email of the authenticated Google account

### Gmail
- `send_email` - Send an email (to, subject, body)
- `create_gmail_label` - Create a new Gmail label
- `list_gmail_labels` - List all user-created labels

### Google Calendar
- `list_calendar_events` - List upcoming events (max_results, days_back)
- `create_calendar_event` - Create an event (summary, start_time, end_time)

### Google Drive
- `list_drive_folders` - List all folders in Google Drive (root or specific parent)
- `search_drive` - Search files by query string

### Google Docs
- `create_document` - Create a new document with optional text
- `get_document` - Get the full text content of a document
- `append_to_document` - Append text to document end
- `search_documents` - Search for documents in Drive
- `export_document` - Export document (text, html, pdf, docx)

### Google Sheets
- `create_spreadsheet` - Create a new spreadsheet
- `read_spreadsheet` - Read data from a range
- `update_spreadsheet` - Update cells with JSON 2D array
- `append_to_spreadsheet` - Append rows to spreadsheet
- `search_spreadsheets` - Search for spreadsheets in Drive
- `get_spreadsheet_info` - Get metadata and dimensions
- `clear_spreadsheet_range` - Clear all values in a range
- `batch_update_spreadsheet` - Batch update multiple ranges
- `add_sheet` - Add a new sheet/tab
- `export_spreadsheet` - Export (csv, xlsx, pdf, tsv)

### Google Slides
- `create_presentation` - Create a new presentation
- `get_presentation` - Get slide metadata and content
- `add_slide` - Add a new slide with layout selection
- `add_text_to_slide` - Add a text box to slide
- `search_presentations` - Search for presentations
- `delete_slide` - Delete a slide by index
- `export_presentation` - Export (pdf, pptx, txt)

---

## 🎯 What's New in v2.1

- **Full Google Workspace Support**: Gmail, Calendar, Drive, Docs, Sheets, and Slides
- **Enhanced Authentication**: OAuth 2.0 with automatic token refresh
- **30+ Tools**: Comprehensive toolset for all Google Workspace services
- **25+ Client Configurations**: Ready-to-use configs for all major MCP clients
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Zero File Mode**: Optional environment variable-based token storage
- **Comprehensive Documentation**: User guides, troubleshooting, and developer docs
- **100% Test Coverage**: Full test suite with pytest

---

## 📦 Installation Options

**Option A: PyPI (Recommended)**
```bash
# Install using pip
pip install gg-mcp

# Set your credentials
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"

# Run the server
gg-mcp
```

**Option B: UVX (Fastest, No Installation)**
```bash
# Set your credentials
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"

# Run directly without installation
uvx gg-mcp
```

**Option C: From Source**
```bash
# Clone the repository
git clone https://github.com/tannht/google-cloud-mcp.git
cd google-cloud-mcp

# Install dependencies
uv sync

# Set your credentials
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"

# Run the server
uv run main.py
```

**Option D: Docker**
```bash
# Clone the repository
git clone https://github.com/tannht/google-cloud-mcp.git
cd google-cloud-mcp

# Copy and configure environment file
cp .env.example .env
# Edit .env with your GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET

# Run with Docker Compose
docker-compose up -d --build

# Access the authentication portal at http://localhost:3838
```

---

## 🔑 Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `GOOGLE_CLIENT_ID` | Yes | — | OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | — | OAuth 2.0 Client Secret |
| `GOOGLE_TOKEN_PATH` | No | `.token.json` | Token file path |
| `GOOGLE_TOKEN_JSON` | No | — | Token as JSON string |
| `AUTH_PORT` | No | `3838` | Auth portal port |
| `GOOGLE_CREDENTIALS_PATH` | No | `credentials.json` | OAuth credentials JSON file path |

---

## 🔐 Authentication Flow

gg-mcp uses OAuth 2.0 authentication with Google. On first run:

1. **Portal Access**: Server starts a web portal at `http://localhost:3838`
2. **Google Login**: Click "Authorize with Google" and sign in
3. **Grant Permissions**: Allow access to Gmail, Calendar, Drive, Docs, Sheets, and Slides
4. **Token Storage**: Authentication token is automatically saved to `.token.json`
5. **Auto-Refresh**: Token refreshes automatically when needed

**For Docker deployments**: The portal is accessible at `http://localhost:3838` (port mapped in docker-compose.yml)

**Token Management**:
- Tokens are stored locally in `.token.json` by default
- Delete `.token.json` to force re-authentication
- Use `GOOGLE_TOKEN_JSON` environment variable for headless deployments
- Use `GOOGLE_TOKEN_PATH` to specify a custom token location

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| `403: access_denied` | Add your email to **Test users** in OAuth consent screen |
| `401: Invalid credentials` | Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET |
| `Token expired` | Delete `.token.json` and re-authenticate |
| Can't access http://localhost:3838 | Port 3838 in use. Try `AUTH_PORT=8080` |
| `403: API not enabled` | Enable APIs in [Google Cloud Console](https://console.cloud.google.com/apis/library) |
| `redirect_uri_mismatch` | Ensure OAuth app type is **Desktop app**, not Web |
| `ModuleNotFoundError` | Run `uvx --pip install --upgrade gg-mcp` |
| Docker connection issues | Ensure port mapping `-p 3838:3838` is set correctly |

📖 **[Full troubleshooting →](GUIDE.md#troubleshooting)**

---

## 📚 Documentation

- **[GUIDE.md](GUIDE.md)** - Complete user & developer guide
- **[MCP_CLIENTS.md](MCP_CLIENTS.md)** - 25+ MCP client configurations

---

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/tannht/google-cloud-mcp.git
cd google-cloud-mcp

# Install development dependencies
uv sync --group dev

# Copy environment template
cp .env.example .env
# Edit .env with your Google OAuth credentials
```

### Running Tests

```bash
# Run all tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_gmail.py -v

# Run with coverage report
uv run pytest --cov=google_cloud_mcp --cov-report=term-missing

# Run with coverage HTML report
uv run pytest --cov=google_cloud_mcp --cov-report=html
```

### Development Server

```bash
# Set credentials
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"

# Run the server in development mode
uv run main.py
```

### Project Structure

```
google-cloud-mcp/
├── google_cloud_mcp/
│   ├── __init__.py          # Package entry point
│   └── server.py            # MCP server + all tools + OAuth portal
├── tests/
│   ├── conftest.py          # pytest fixtures
│   ├── test_account.py      # Account tests
│   ├── test_calendar.py     # Calendar API tests
│   ├── test_docs.py         # Docs API tests
│   ├── test_drive.py        # Drive API tests
│   ├── test_gmail.py        # Gmail API tests
│   ├── test_sheets_core.py  # Sheets core tests
│   ├── test_sheets_extra.py # Sheets extra operations
│   └── test_slides.py       # Slides API tests
├── main.py                  # CLI entry point
├── pyproject.toml           # Project config
├── docker-compose.yml       # Docker Compose setup
├── Dockerfile               # Container build
├── .env.example             # Environment variable template
├── GUIDE.md                 # Complete user & developer guide
├── MCP_CLIENTS.md           # Client configuration guide
└── README.md                # This file
```

📖 **[Dev setup →](GUIDE.md#for-developers---setup)**

---

## 📄 License

MIT

## 👥 Contributors

- **Hoang Tan** (Owner)
- **PubPug Assistant** (Primary Developer)
