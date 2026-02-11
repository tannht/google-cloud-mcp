# 🐶 Google Cloud MCP (FastMCP Edition)

![License](https://img.shields.io/github/license/tannht/google-cloud-mcp)
![Build](https://img.shields.io/github/workflow/status/tannht/google-cloud-mcp/Main%20Workflow)

Bộ Model Context Protocol (MCP) server "hàng tự trồng" siêu nhanh, siêu nhẹ được xây dựng bằng **FastMCP** và **Python**. Giúp AI của bạn (như PubPug) có thể thao tác trực tiếp với các dịch vụ của Google Cloud & Workspace.

## 🚀 Tính năng nổi bật

### 📧 Gmail
- **`create_gmail_label`**: Tạo nhãn Gmail cực nhanh.
- **`send_email`**: Gửi email chuyên nghiệp qua API.
- **`clean_spam`**: "Đớp" sạch thư rác chỉ trong 1 nốt nhạc.
- **`list_gmail_labels`**: Liệt kê toàn bộ nhãn người dùng.

### 📂 Google Drive
- **`search_drive`**: Đánh hơi và tìm kiếm file trên Drive bằng từ khóa.

## 🛠️ Cài đặt & Sử dụng

### Yêu cầu hệ thống
- **Python 3.10+**
- **UV** (Công cụ quản lý Python siêu tốc)

### Cài đặt môi trường
```bash
# Clone repo
git clone https://github.com/tannht/google-cloud-mcp.git
cd google-cloud-mcp

# Cài đặt dependency bằng uv
uv sync
```

### Cấu hình MCP Client (Ví dụ: OpenClaw / Claude Desktop)
Thêm đoạn sau vào file cấu hình MCP của bạn:

```json
"google-claude": {
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

## 🔐 Bảo mật (Security)
- File `credentials.json` và `token.json` được bảo mật nghiêm ngặt và đã được thêm vào `.gitignore`.
- Sử dụng OAuth 2.0 theo đúng tiêu chuẩn của Google.

## 🐕 Tác giả
Phát triển bởi **Sếp Meo Meo** và trợ lý trung thành **PubPug 🐶**.

---
*Gâu gâu! Code này được bảo vệ bởi răng của PubPug!* 🦴
