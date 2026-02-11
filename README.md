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
- **Organization**: Keep your professional and personal life perfectly synced.

### 📂 Cloud Storage & Productivity (Drive, Docs, Sheets, Slides)
- **Drive**: Semantic file search and metadata retrieval.
- **Docs**: Programmatic document generation and content manipulation.
- **Sheets**: Automated data logging, financial tracking, and spreadsheet management.
- **Slides**: Dynamic presentation creation and slide orchestration.

## 🔐 Authentication & Security

- **Web Auth Portal (v1.6+)**: Seamless authentication via `http://localhost:3838`. No manual code copying required.
- **No-File Mode**: Supports `GOOGLE_TOKEN_JSON` environment variable for stateless deployments (Docker/Cloud).
- **GPG Signed**: Every commit is cryptographically signed for end-to-end integrity.

## 🛠️ Quick Start

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
