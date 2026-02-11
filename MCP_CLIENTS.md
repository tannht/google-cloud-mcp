# MCP Client Configuration Guide

This guide covers how to configure **Google Cloud MCP** for every major MCP-compatible client.

> Replace `/path/to/google-cloud-mcp` with the actual absolute path to your cloned repository.

---

## Claude Code

**CLI command:**

```bash
claude mcp add google-cloud-mcp \
  -e GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com \
  -e GOOGLE_CLIENT_SECRET=your-client-secret \
  -- uv run --directory /path/to/google-cloud-mcp server.py
```

**Or manually create `.mcp.json` in your project root:**

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

---

## Claude Desktop

**File:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

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

---

## Cursor

**File:** `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project)

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

---

## VS Code (Copilot)

**File:** `.vscode/mcp.json` in your workspace

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

---

## Visual Studio 2022

**Path:** Tools > Options > GitHub Copilot > MCP Servers

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

---

## Copilot Coding Agent

**Path:** Repository > Settings > Copilot > Coding agent > MCP configuration

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

---

## Copilot CLI

**File:** `~/.copilot/mcp-config.json`

```json
{
  "mcpServers": {
    "google-cloud-mcp": {
      "type": "local",
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

---

## Windsurf

**File:** `~/.codeium/windsurf/mcp_config.json`

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

---

## Kiro

**File:** `.kiro/settings/mcp.json` in your project

```json
{
  "mcpServers": {
    "google-cloud-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/google-cloud-mcp", "server.py"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

---

## Kilo Code

**File:** `.kilocode/mcp.json` in your project

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

---

## Cline / Roo Code

**Path:** MCP Server panel > Edit MCP Settings

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

---

## JetBrains AI Assistant

**Path:** Settings > Tools > AI Assistant > Model Context Protocol (MCP) > Add > As JSON

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

---

## Gemini CLI

**File:** `~/.gemini/settings.json`

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

---

## OpenAI Codex

**File:** `codex.toml` or `~/.codex/config.toml`

```toml
[mcp_servers.google-cloud-mcp]
command = "uv"
args = ["run", "--directory", "/path/to/google-cloud-mcp", "server.py"]

[mcp_servers.google-cloud-mcp.env]
GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-client-secret"
```

---

## Augment Code

**File:** VS Code `settings.json`

```json
{
  "augment.advanced": {
    "mcpServers": [
      {
        "name": "google-cloud-mcp",
        "command": "uv",
        "args": ["run", "--directory", "/path/to/google-cloud-mcp", "server.py"],
        "env": {
          "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
          "GOOGLE_CLIENT_SECRET": "your-client-secret"
        }
      }
    ]
  }
}
```

---

## Zed

**File:** `~/.config/zed/settings.json`

```json
{
  "context_servers": {
    "google-cloud-mcp": {
      "command": {
        "path": "uv",
        "args": ["run", "--directory", "/path/to/google-cloud-mcp", "server.py"],
        "env": {
          "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
          "GOOGLE_CLIENT_SECRET": "your-client-secret"
        }
      }
    }
  }
}
```

---

## Trae

**Path:** Settings > MCP > Add manually

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

---

## Opencode

```json
{
  "mcp": {
    "google-cloud-mcp": {
      "type": "local",
      "command": ["uv", "run", "--directory", "/path/to/google-cloud-mcp", "server.py"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret"
      },
      "enabled": true
    }
  }
}
```

---

## Qwen Code

**File:** `~/.qwen/settings.json` (global) or `.qwen/settings.json` (project)

**CLI command:**

```bash
qwen mcp add google-cloud-mcp \
  --command uv \
  --args '["run", "--directory", "/path/to/google-cloud-mcp", "server.py"]' \
  --scope user
```

**Or manually:**

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

---

## Amazon Q Developer CLI

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

---

## Warp

**Path:** Settings > AI > Manage MCP servers

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

---

## Amp

```bash
amp mcp add google-cloud-mcp \
  -- uv run --directory /path/to/google-cloud-mcp server.py
```

---

## LM Studio

**Path:** Program > Install > Edit mcp.json

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

---

## Perplexity Desktop

**Path:** Perplexity > Settings > Connectors > Add MCP

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

---

## Using Docker (any client)

Replace the `command` and `args` in any configuration above:

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

---

## Windows Users

If you are on Windows, wrap the command with `cmd`:

```json
{
  "mcpServers": {
    "google-cloud-mcp": {
      "command": "cmd",
      "args": ["/c", "uv", "run", "--directory", "C:\\path\\to\\google-cloud-mcp", "server.py"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```
