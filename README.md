# 🐶 Google Cloud MCP (FastMCP Edition)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by PubPug](https://img.shields.io/badge/Powered%20By-PubPug%20Assistant-orange)](https://github.com/tannht/google-cloud-mcp)
[![Docker Support](https://img.shields.io/badge/Docker-Supported-blue.svg?logo=docker)](https://www.docker.com/)

A high-performance Model Context Protocol (MCP) server implementation designed to empower AI agents with seamless integration into Google Cloud and Workspace ecosystems. Built with **FastMCP** and optimized for **UV** and **Docker**.

## 🚀 Key Capabilities

### 📧 Intelligent Gmail Orchestration
- **`create_gmail_label`**: Programmatically generate Gmail labels for automated organization.
- **`batch_label_emails`**: Apply labels to historical emails based on search queries.
- **`create_gmail_filter`**: Establish automated routing rules for incoming communications.
- **`send_email`**: Execute professional email communication via secure API protocols.
- **`clean_spam`**: Automated garbage collection to maintain a pristine inbox.

### 📂 Cloud Storage Integration (Google Drive)
- **`search_drive`**: Advanced semantic search and metadata retrieval for files stored across Google Drive.

## 🔐 Authentication Made Easy (v1.6+)

Setting up Google access is now simpler than ever. No more manual code copying!

1.  **Configure Credentials**: Add your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to the `.env` file.
2.  **Start the Server**: Run `uv run server.py`.
3.  **Access Web Portal**: Open your browser and navigate to **`http://localhost:3838`**.
4.  **One-Click Authorize**: Click the **"Authorize with Google"** button and grant permissions.
5.  **Done!**: The server automatically captures the token and saves it to `.token.json`. Your AI is now connected.

## 🛠️ Deployment & Architecture

### Docker Deployment (Recommended)
The fastest way to deploy the server is using Docker Compose:

```bash
# Build and start the container
docker-compose up -d --build
```

### Local Development
Prerequisites:
- **Python 3.10+**
- **UV** (High-speed Python package manager)

```bash
# Clone the repository
git clone https://github.com/tannht/google-cloud-mcp.git
cd google-cloud-mcp

# Sync environment and dependencies
uv sync

# Run the server
uv run server.py
```

## ⚙️ MCP Client Configuration

> **Full guide for 25+ clients:** **[MCP_CLIENT.md](MCP_CLIENTS.md)**
>
> Covers Claude Code, Claude Desktop, Cursor, VS Code, Windsurf, Kiro, Kilo Code, Cline, Roo Code, JetBrains, Gemini CLI, OpenAI Codex, Zed, Augment Code, Warp, Amp, LM Studio, Perplexity, Qwen Code, Amazon Q, and more.

Below are quick-start examples. Replace `/path/to/google-cloud-mcp` with your actual path.

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude mcp add google-cloud-mcp \
  -e GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com \
  -e GOOGLE_CLIENT_SECRET=your-client-secret \
  -- uv run --directory /path/to/google-cloud-mcp server.py
```
</details>

<details>
<summary><strong>Claude Desktop</strong></summary>

File: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "google-cloud-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/google-cloud-mcp", "server.py"],
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
<summary><strong>Cursor</strong></summary>

File: `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project)

```json
{
  "mcpServers": {
    "google-cloud-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/google-cloud-mcp", "server.py"],
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
<summary><strong>VS Code (Copilot)</strong></summary>

File: `.vscode/mcp.json`

```json
{
  "servers": {
    "google-cloud-mcp": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/google-cloud-mcp", "server.py"],
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
<summary><strong>Docker (any client)</strong></summary>

```json
{
  "mcpServers": {
    "google-cloud-mcp": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GOOGLE_CLIENT_ID",
        "-e", "GOOGLE_CLIENT_SECRET",
        "-v", "/path/to/google-cloud-mcp/.token.json:/app/.token.json",
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

## 🐕 Attribution
Developed and maintained by **PubPug Assistant 🐶**.

---
*Optimized for the next generation of AI Workflows.*
