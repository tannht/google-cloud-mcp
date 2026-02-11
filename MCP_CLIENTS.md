# MCP Client Configuration Guide

Complete configuration guide for **gg-mcp** across all major MCP-compatible clients.

Each client section shows two methods:
- **`uvx` (Recommended)** — Install from PyPI, no path needed
- **From Source** — For development, requires cloning the repo

> Replace `/path/to/google-cloud-mcp` with the actual absolute path to your cloned repository (only needed for "From Source" method).

---

## Claude Code

**uvx (Recommended):**

```bash
claude mcp add gg-mcp \
  -e GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com \
  -e GOOGLE_CLIENT_SECRET=your-client-secret \
  -- uvx gg-mcp
```

**From Source:**

```bash
claude mcp add gg-mcp \
  -e GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com \
  -e GOOGLE_CLIENT_SECRET=your-client-secret \
  -- uv run --directory /path/to/google-cloud-mcp server.py
```

---

## Claude Desktop

**File:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

**uvx (Recommended):**

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

<details>
<summary>From Source</summary>

```json
{
  "mcpServers": {
    "gg-mcp": {
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

---

## Cursor

**File:** `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project)

**uvx (Recommended):**

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

<details>
<summary>From Source</summary>

```json
{
  "mcpServers": {
    "gg-mcp": {
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

---

## VS Code (Copilot)

**File:** `.vscode/mcp.json` in your workspace

**uvx (Recommended):**

```json
{
  "servers": {
    "gg-mcp": {
      "type": "stdio",
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

<details>
<summary>From Source</summary>

```json
{
  "servers": {
    "gg-mcp": {
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

---

## Visual Studio 2022

**Path:** Tools > Options > GitHub Copilot > MCP Servers

```json
{
  "servers": {
    "gg-mcp": {
      "type": "stdio",
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

---

## Copilot Coding Agent

**Path:** Repository > Settings > Copilot > Coding agent > MCP configuration

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

---

## Copilot CLI

**File:** `~/.copilot/mcp-config.json`

```json
{
  "mcpServers": {
    "gg-mcp": {
      "type": "local",
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

---

## Windsurf

**File:** `~/.codeium/windsurf/mcp_config.json`

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

---

## Kiro

**File:** `.kiro/settings/mcp.json` in your project

```json
{
  "mcpServers": {
    "gg-mcp": {
      "command": "uvx",
      "args": ["gg-mcp"],
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

---

## Cline / Roo Code

**Path:** MCP Server panel > Edit MCP Settings

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

---

## JetBrains AI Assistant

**Path:** Settings > Tools > AI Assistant > Model Context Protocol (MCP) > Add > As JSON

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

---

## Gemini CLI

**File:** `~/.gemini/settings.json`

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

---

## OpenAI Codex

**File:** `codex.toml` or `~/.codex/config.toml`

```toml
[mcp_servers.gg-mcp]
command = "uvx"
args = ["gg-mcp"]

[mcp_servers.gg-mcp.env]
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
        "name": "gg-mcp",
        "command": "uvx",
        "args": ["gg-mcp"],
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
    "gg-mcp": {
      "command": {
        "path": "uvx",
        "args": ["gg-mcp"],
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

---

## Opencode

```json
{
  "mcp": {
    "gg-mcp": {
      "type": "local",
      "command": ["uvx", "gg-mcp"],
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
qwen mcp add gg-mcp \
  --command uvx \
  --args '["gg-mcp"]' \
  --scope user
```

**Or manually:**

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

---

## Amazon Q Developer CLI

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

---

## Warp

**Path:** Settings > AI > Manage MCP servers

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

---

## Amp

```bash
amp mcp add gg-mcp -- uvx gg-mcp
```

---

## LM Studio

**Path:** Program > Install > Edit mcp.json

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

---

## Perplexity Desktop

**Path:** Perplexity > Settings > Connectors > Add MCP

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

---

## Using Docker (any client)

Replace the `command` and `args` in any configuration above:

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

---

## Windows Users

If `uvx` is not in your PATH on Windows, wrap with `cmd`:

```json
{
  "mcpServers": {
    "gg-mcp": {
      "command": "cmd",
      "args": ["/c", "uvx", "gg-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```
