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

### Google Ads
Requires `GOOGLE_ADS_DEVELOPER_TOKEN` (see `.env.example`) and the Google Ads API enabled in your Cloud project.
- `list_ads_accounts` - List accessible Google Ads accounts
- `ads_search` - Run any GAQL query
- `list_ads_campaigns` - List campaigns with daily budget (optional status filter)
- `get_ads_campaign_performance` - Impressions, clicks, cost, conversions per campaign
- `set_ads_campaign_status` - Pause or enable a campaign

### Google Search Console
Enable the Search Console API in your Cloud project.
- `list_search_console_sites` - List properties
- `search_console_query` - Search analytics (clicks, impressions, CTR, position)
- `list_search_console_sitemaps` - List submitted sitemaps
- `inspect_url` - URL Inspection (index status)
- `add_search_console_site` - Add a property
- `submit_search_console_sitemap` - Submit a sitemap

### Google Analytics (GA4)
Enable the Analytics Data API and Analytics Admin API in your Cloud project.
- `list_ga4_properties` - List accounts and properties
- `run_ga4_report` - Run a report (metrics, dimensions, date range)
- `run_ga4_realtime_report` - Realtime report (last 30 minutes)
- `list_ga4_data_streams` - Data streams and measurement IDs
- `list_ga4_key_events` - Key events (conversions)
- `get_ga4_metadata` - Available dimension/metric names

### Google Tag Manager
Enable the Tag Manager API in your Cloud project.
- `list_gtm_accounts`, `list_gtm_containers`, `list_gtm_workspaces` - Browse accounts, containers, workspaces
- `list_gtm_tags`, `list_gtm_triggers`, `list_gtm_variables` - Workspace contents
- `get_gtm_live_version` - Currently published version
- `create_gtm_version` - Create a version from a workspace (not published)
- `publish_gtm_version` - Publish a version live

> **Upgrading:** these services add OAuth scopes (`adwords`, `webmasters`, `analytics.readonly`, `tagmanager.*`). Delete `.token.json` and re-authorize at http://localhost:3838.

### Google Slides
- `create_presentation` - Create a new presentation
- `get_presentation` - Get slide metadata and content
- `add_slide` - Add a new slide with layout selection
- `add_text_to_slide` - Add a text box to slide
- `search_presentations` - Search for presentations
- `delete_slide` - Delete a slide by index
- `export_presentation` - Export (pdf, pptx, txt)

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

📖 **[25+ client configs →](MCP_CLIENTS.md)**

---

## 📦 Installation Options

**Option A: PyPI (Recommended)**
```bash
pip install gg-mcp
export GOOGLE_CLIENT_ID="..."
export GOOGLE_CLIENT_SECRET="..."
gg-mcp
```

**Option B: From Source**
```bash
git clone https://github.com/tannht/google-cloud-mcp.git
cd google-cloud-mcp
uv sync
export GOOGLE_CLIENT_ID="..."
export GOOGLE_CLIENT_SECRET="..."
uv run main.py
```

**Option C: Docker**
```bash
git clone https://github.com/tannht/google-cloud-mcp.git
cd google-cloud-mcp
docker-compose up -d --build
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

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| `403: access_denied` | Add your email to **Test users** in OAuth consent screen |
| `401: Invalid credentials` | Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET |
| `Token expired` | Delete `.token.json` and re-authenticate |
| Can't access http://localhost:3838 | Port 3838 in use. Try `AUTH_PORT=8080` |
| `403: API not enabled` | Enable APIs in [Google Cloud Console](https://console.cloud.google.com/apis/library) |

📖 **[Full troubleshooting →](GUIDE.md#troubleshooting)**

---

## 📚 Documentation

- **[GUIDE.md](GUIDE.md)** - Complete user & developer guide
- **[MCP_CLIENTS.md](MCP_CLIENTS.md)** - 25+ MCP client configurations

---

## 🛠️ Development

```bash
git clone https://github.com/tannht/google-cloud-mcp.git
cd google-cloud-mcp
uv sync --group dev
uv run pytest -v  # Run tests
```

📖 **[Dev setup →](GUIDE.md#for-developers---setup)**

---

## 📄 License

MIT

## 👥 Contributors

- **Hoang Tan** (Owner)
- **PubPug Assistant** (Primary Developer)
