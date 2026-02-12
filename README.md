# 🐶 Google Cloud MCP (FastMCP Elite Edition v2.0)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by PubPug](https://img.shields.io/badge/Powered%20By-PubPug%20Assistant-orange)](https://github.com/tannht/google-cloud-mcp)
[![Docker Support](https://img.shields.io/badge/Docker-Supported-blue.svg?logo=docker)](https://www.docker.com/)
[![Verified Commit](https://img.shields.io/badge/Commits-GPG--Verified-brightgreen)](https://github.com/tannht/google-cloud-mcp/commits/main)

A high-performance, enterprise-grade Model Context Protocol (MCP) server designed to empower AI agents with deep, seamless integration into the entire Google Workspace ecosystem.

## 🚀 Key Capabilities

### 📧 Intelligent Gmail Orchestration
- **Automation**: Programmatically generate labels and routing filters.
- **Cleanup**: Advanced spam detection and automated garbage collection.
- **Communication**: Execute professional email sequences via secure API protocols.

### 📅 Advanced Calendar Management
- **Scheduling**: List, create, and manage events with full Timezone support (Asia/Ho_Chi_Minh).

### 📂 Cloud Storage & Productivity (Drive, Docs, Sheets, Slides)
- **Drive**: Semantic file search and metadata retrieval.
- **Docs/Sheets/Slides**: Programmatic generation and manipulation of workspace documents.

## 🔐 Authentication & Security

- **Web Auth Portal**: Seamless authentication via `http://localhost:3838`.
- **No-File Mode**: Supports `GOOGLE_TOKEN_JSON` for stateless deployments.
- **GPG Signed**: Every commit is cryptographically signed for end-to-end integrity.

## 🛠️ MCP Client Configuration

To use this server with your favorite AI tools, add the following configuration:

### 1. Claude Desktop
Edit your `claude_desktop_config.json` (usually in `%APPDATA%\Claude` or `~/Library/Application Support/Claude`):

```json
{
  "mcpServers": {
    "google-cloud": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/absolute/path/to/google-cloud-mcp",
        "/absolute/path/to/google-cloud-mcp/main.py"
      ],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id",
        "GOOGLE_CLIENT_SECRET": "your-client-secret",
        "GOOGLE_TOKEN_JSON": "your-token-json-if-applicable"
      }
    }
  }
}
```

### 2. Cursor IDE
1. Go to **Settings** -> **Features** -> **MCP Servers**.
2. Click **+ Add New MCP Server**.
3. Name: `google-cloud`.
4. Type: `stdio`.
5. Command: `uv run --project /path/to/google-cloud-mcp /path/to/google-cloud-mcp/main.py`.

### 3. OpenClaw
Add to your `openclaw.json` under the `mcpServers` section:
```json
"google-claude": {
  "type": "stdio",
  "command": "uv",
  "args": ["run", "--project", "/root/PROJECTS/google-cloud-mcp", "/root/PROJECTS/google-cloud-mcp/main.py"]
}
```

## 🚀 Deployment

### Docker (Recommended)
```bash
docker-compose up -d --build
```

### Local Development
```bash
uv sync
uv run main.py
```

## 🐕 Attribution
Developed and maintained by **PubPug Assistant 🐶** for the **AI Dream Team**.

---
*Standardizing the future of AI-Human collaboration.*
