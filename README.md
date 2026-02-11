# 🐶 Google Cloud MCP (FastMCP Edition)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by PubPug](https://img.shields.io/badge/Powered%20By-PubPug%20Assistant-orange)](https://github.com/tannht/google-cloud-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A high-performance Model Context Protocol (MCP) server implementation designed to empower AI agents with seamless integration into Google Cloud and Workspace ecosystems. Built with **FastMCP** and optimized for **UV** package management.

## 🚀 Key Capabilities

### 📧 Intelligent Gmail Orchestration
- **`create_gmail_label`**: Programmatically generate Gmail labels for automated organization.
- **`send_email`**: Execute professional email communication via secure API protocols.
- **`clean_spam`**: Automated garbage collection to maintain a pristine inbox.
- **`list_gmail_labels`**: Retrieve full directory of user-defined labels.

### 📂 Cloud Storage Integration (Google Drive)
- **`search_drive`**: Advanced semantic search and metadata retrieval for files stored across Google Drive.

## 🛠️ Deployment & Architecture

### Prerequisites
- **Python 3.10+**
- **UV** (High-speed Python package manager and resolver)

### Environment Setup
```bash
# Clone the repository
git clone https://github.com/tannht/google-cloud-mcp.git
cd google-cloud-mcp

# Sync environment and dependencies
uv sync
```

### MCP Client Configuration (OpenClaw / Claude Desktop)
Integrate the following configuration into your MCP client settings:

```json
"google-cloud": {
  "type": "stdio",
  "command": "uv",
  "args": [
    "run",
    "--project",
    "/root/PROJECTS/google-cloud-mcp",
    "/root/PROJECTS/google-cloud-mcp/server.py"
  ]
}
```

## 🔐 Enterprise Security
- **OAuth 2.0 Compliant**: Adheres to industry-standard authorization protocols.
- **Secret Management**: Sensitive credentials (`credentials.json`, `token.json`) are strictly excluded via `.gitignore`.
- **Stateless Design**: Optimized for reliable STDIO transport.

## 🐕 Attribution
Developed and maintained by **PubPug Assistant 🐶**.

---
*Optimized for the next generation of AI Workflows.*
