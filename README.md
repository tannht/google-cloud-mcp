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
- **UV** (High-speed Python package manager and resolver)

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
- **Dockerized Isolation**: Enhances security via containerized execution environments.

## 🐕 Attribution
Developed and maintained by **PubPug Assistant 🐶**.

---
*Optimized for the next generation of AI Workflows.*
