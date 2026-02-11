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

## Available Tools

### Account
| Tool | Description |
|------|-------------|
| `get_account_info` | Get the email address of the authenticated Google account |

### Gmail
| Tool | Description |
|------|-------------|
| `send_email` | Send an email (to, subject, body) |
| `create_gmail_label` | Create a new Gmail label |
| `list_gmail_labels` | List all user-created labels |

### Google Calendar
| Tool | Description |
|------|-------------|
| `list_calendar_events` | List upcoming events (with optional `max_results` and `days_back`) |
| `create_calendar_event` | Create an event (summary, start_time, end_time in `YYYY-MM-DDTHH:MM` format) |

### Google Drive
| Tool | Description |
|------|-------------|
| `search_drive` | Search files by query string |

### Google Docs
| Tool | Description |
|------|-------------|
| `create_document` | Create a new document with optional initial text |
| `get_document` | Get the full text content of a document |
| `append_to_document` | Append text to the end of a document |
| `search_documents` | Search for documents in Drive |
| `export_document` | Export a document (text, html, pdf, docx) |

### Google Sheets
| Tool | Description |
|------|-------------|
| `create_spreadsheet` | Create a new spreadsheet |
| `read_spreadsheet` | Read data from a range (e.g. `Sheet1!A1:D10`) |
| `update_spreadsheet` | Update cells with JSON 2D array values |
| `append_to_spreadsheet` | Append rows to a spreadsheet |
| `search_spreadsheets` | Search for spreadsheets in Drive |
| `get_spreadsheet_info` | Get metadata, sheet names, and dimensions |
| `clear_spreadsheet_range` | Clear all values in a range |
| `batch_update_spreadsheet` | Batch update multiple ranges at once |
| `add_sheet` | Add a new sheet/tab to an existing spreadsheet |
| `export_spreadsheet` | Export a spreadsheet (csv, xlsx, pdf, tsv) |

### Google Slides
| Tool | Description |
|------|-------------|
| `create_presentation` | Create a new presentation |
| `get_presentation` | Get slide metadata and text content |
| `add_slide` | Add a new slide with layout selection |
| `add_text_to_slide` | Add a text box to a specific slide |
| `search_presentations` | Search for presentations in Drive |
| `delete_slide` | Delete a slide by index |
| `export_presentation` | Export a presentation (pdf, pptx, txt) |

---

## Prerequisites

### 1. Create Google Cloud OAuth Credentials

You need a Google Cloud project with OAuth 2.0 credentials. Follow these steps:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Navigate to **APIs & Services > OAuth consent screen**
   - Choose **External** user type
   - Fill in app name and support email
   - Under **Scopes**, click **Add or Remove Scopes** and add all of the following:
     ```
     https://www.googleapis.com/auth/gmail.modify
     https://www.googleapis.com/auth/gmail.labels
     https://www.googleapis.com/auth/gmail.settings.basic
     https://www.googleapis.com/auth/drive
     https://www.googleapis.com/auth/calendar
     https://www.googleapis.com/auth/documents
     https://www.googleapis.com/auth/spreadsheets
     https://www.googleapis.com/auth/presentations
     ```
     > You can paste them all at once in the **"Manually add scopes"** text box (one per line or comma-separated).
   - Add your email to **Test users** (required while app is in "Testing" status)
4. Navigate to **APIs & Services > Credentials**
   - Click **Create Credentials > OAuth client ID**
   - Application type: **Desktop app**
   - Copy the **Client ID** and **Client Secret**

### 2. Enable Required Google APIs

In the [API Library](https://console.cloud.google.com/apis/library), enable these APIs for your project:

| API | Required For |
|-----|-------------|
| **Gmail API** | `send_email`, `create_gmail_label`, `list_gmail_labels`, `get_account_info` |
| **Google Calendar API** | `list_calendar_events`, `create_calendar_event` |
| **Google Drive API** | `search_drive`, `search_documents`, `search_spreadsheets`, `search_presentations`, exports |
| **Google Docs API** | `create_document`, `get_document`, `append_to_document` |
| **Google Sheets API** | `create_spreadsheet`, `read_spreadsheet`, `update_spreadsheet`, and other Sheets tools |
| **Google Slides API** | `create_presentation`, `get_presentation`, `add_slide`, and other Slides tools |

> **Tip:** You only need to enable the APIs for the services you plan to use.

### 3. OAuth Scopes Requested

When you authorize, the server requests the following permissions:

| Scope | Purpose |
|-------|---------|
| `gmail.modify` | Read and send emails |
| `gmail.labels` | Manage labels |
| `gmail.settings.basic` | Read Gmail settings |
| `drive` | Search files in Google Drive |
| `calendar` | Read and create calendar events |
| `documents` | Google Docs access |
| `spreadsheets` | Google Sheets access |
| `presentations` | Google Slides access |

---

## Quick Start

### Option A: Install from PyPI (Recommended)

No cloning, no path configuration:

```bash
pip install gg-mcp
```

Then configure your MCP client (see below).

### Option B: From Source

```bash
git clone https://github.com/tannht/google-cloud-mcp.git
cd google-cloud-mcp
cp .env.example .env
# Edit .env with your GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
uv sync
uv run main.py
```

### Option C: Docker

```bash
cp .env.example .env
# Edit .env with your credentials
docker-compose up -d --build
```

---

## Authentication

On first run, the server starts a web portal at **http://localhost:3838**:

1. Open `http://localhost:3838` in your browser
2. Click **"Authorize with Google"**
3. Grant the requested permissions
4. Token is saved automatically to `.token.json`

After initial auth, the token refreshes automatically. No manual steps needed.

---

## MCP Client Configuration

> **Full guide for 25+ clients:** **[MCP_CLIENTS.md](MCP_CLIENTS.md)**

### Using `uvx` (Recommended - No Path Needed)

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude mcp add gg-mcp \
  -e GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com \
  -e GOOGLE_CLIENT_SECRET=your-client-secret \
  -- uvx gg-mcp
```
</details>

<details>
<summary><strong>Claude Desktop</strong></summary>

File: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

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
</details>

<details>
<summary><strong>Cursor / VS Code / Any MCP Client</strong></summary>

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
</details>

### From Source (for development)

<details>
<summary><strong>Any MCP Client (uv run)</strong></summary>

Replace `/path/to/google-cloud-mcp` with your actual path.

```json
{
  "mcpServers": {
    "gg-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/google-cloud-mcp", "main.py"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```
</details>

<details>
<summary><strong>Docker</strong></summary>

```json
{
  "mcpServers": {
    "gg-mcp": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GOOGLE_CLIENT_ID",
        "-e", "GOOGLE_CLIENT_SECRET",
        "-p", "3838:3838",
        "google-cloud-mcp"
      ],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```
</details>

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_CLIENT_ID` | Yes | — | OAuth 2.0 Client ID from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Yes | — | OAuth 2.0 Client Secret |
| `GOOGLE_TOKEN_PATH` | No | `.token.json` | Path to saved OAuth token file |
| `GOOGLE_TOKEN_JSON` | No | — | Token as inline JSON string (alternative to file) |
| `GOOGLE_CREDENTIALS_PATH` | No | `credentials.json` | Path to credentials JSON file (fallback) |
| `AUTH_PORT` | No | `3838` | Port for the authentication web portal |

---

## Development

### Project Structure

```
google-cloud-mcp/
├── google_cloud_mcp/
│   ├── __init__.py          # Package entry point, exports main()
│   └── server.py            # MCP server implementation (all tools + OAuth portal)
├── tests/
│   ├── conftest.py          # Shared pytest fixtures (mock Google services)
│   ├── test_account.py      # Account info tests
│   ├── test_calendar.py     # Calendar API tests
│   ├── test_docs.py         # Docs API tests
│   ├── test_drive.py        # Drive API tests
│   ├── test_gmail.py        # Gmail API tests
│   ├── test_sheets_core.py  # Sheets core tests
│   ├── test_sheets_extra.py # Sheets extra operations tests
│   └── test_slides.py       # Slides API tests
├── main.py                  # CLI entry point wrapper
├── pyproject.toml           # Project config, dependencies, scripts
├── docker-compose.yml       # Docker Compose setup
├── Dockerfile               # Container build
├── .env.example             # Environment variable template
└── MCP_CLIENTS.md           # Client configuration guide (25+ clients)
```

### Setup

```bash
git clone https://github.com/tannht/google-cloud-mcp.git
cd google-cloud-mcp
uv sync --group dev
cp .env.example .env
# Edit .env with your GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_gmail.py -v

# Run with coverage report
uv run pytest --cov=google_cloud_mcp --cov-report=term-missing
```

### VS Code Debugging

The project includes `.vscode/launch.json` with pre-configured debug profiles:

| Configuration | Description |
|---|---|
| **Run MCP Server** | Launch the MCP server (`google_cloud_mcp` module) |
| **Run main.py** | Run the `main.py` entry point |
| **Python: Current File** | Debug the currently open Python file |
| **Pytest: All Tests** | Run all tests in `tests/` with verbose output |
| **Pytest: Current File** | Run tests in the currently open test file |
| **Pytest: With Coverage** | Run all tests with coverage report |

Open the **Run & Debug** panel (`Ctrl+Shift+D` / `Cmd+Shift+D`) and select a configuration from the dropdown.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `403: access_denied` | Add your email to **Test users** in OAuth consent screen |
| `403: API not enabled` | Enable the required API in [API Library](https://console.cloud.google.com/apis/library) |
| `Token expired` | Delete `.token.json` and re-authorize via `http://localhost:3838` |
| `redirect_uri_mismatch` | Ensure OAuth app type is **Desktop app**, not Web |

---

## License

MIT

## Contributors

- **Hoang Tan** (Owner)
- **PubPug Assistant** (Primary Developer)

*(pubpug@metoolzy.com)*
