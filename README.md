# Platform MCP Server

A personal Model Context Protocol (MCP) server that wraps platform engineering tools (Ansible, Kubernetes, Flux, Git) into secure, idempotent commands for AI agents.

## 🎯 Purpose

This MCP server acts as a "constitution" and "long-term memory" for AI agents, providing:
- **Security-first** tool wrappers (no shell injection, validated inputs)
- **Idempotent** operations (check-before-change patterns)
- **Clear documentation** (every tool has detailed docstrings and type hints)
- **Self-improving** architecture (tools can call other tools)

## 🏗️ Architecture

```
User Prompt → AI Agent (Zed/Claude) → Augmented Prompt → LLM
                                      (Prompt + Constitution + Tool Manifest)
                                                ↓
                                           MCP Server (platform_mcp.py)
                                                ↓
                                      Safe, Validated Commands
```

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python3 --version

# Install dependencies
pip install mcp fastmcp

# Ensure platform tools are available
kubectl version --client
ansible --version
flux --version
```

### Installation

```bash
# Clone this repo
git clone https://github.com/scatat/platform-mcp-server.git
cd platform-mcp-server

# Make executable
chmod +x platform_mcp.py

# Test the server
python platform_mcp.py
```

### Configure Your AI Agent

Add to your MCP client configuration (e.g., Claude Desktop, Zed):

```json
{
  "mcpServers": {
    "platform-tools": {
      "command": "python3",
      "args": ["/path/to/platform-mcp-server/platform_mcp.py"]
    }
  }
}
```

## 📚 Available Tools

### V1: Read-Only Tools (Safe, No Side Effects)

| Tool | Description | Status |
|------|-------------|--------|
| `list_kube_contexts` | List available Kubernetes contexts | ✅ Implemented |

### V2: Planned Tools

- `run_flux_on_prod` - Execute Flux reconciliation
- `list_ansible_packages` - Show packages in Ansible inventory
- `get_git_status` - Check repository status
- `list_teleport_apps` - Show Teleport applications

### V3: Write Tools (Idempotent Operations)

- `install_package` - Add package to Ansible playbook (with duplicate check)
- `create_flux_kustomization` - Create new Flux resource
- `update_git_repo` - Commit and push changes

## 🔒 Security Principles

Every tool in this server follows these rules:

1. **No `shell=True`**: Always use `subprocess.run(..., shell=False)`
2. **Input validation**: All user inputs validated against allow-lists or regex
3. **Use `shlex.split()`**: For safe command parsing
4. **Clear error messages**: Tools return actionable error info
5. **Read-only first**: Start with safe, read-only tools before write operations

## 🎓 Learning Resources

This project is designed for platform engineers learning Python:

- **Detailed comments**: Every section explained with analogies
- **Type hints**: Clear API contracts
- **Docstrings**: Comprehensive tool documentation
- **Security examples**: Shows safe vs. unsafe patterns

## 📖 Core Principles

1. **Clarity over Cuteness**: Simple, readable Python with analogies
2. **Security is Non-Negotiable**: No shortcuts on input validation
3. **Docstrings & Type Hints are our API**: The AI reads these to understand tools
4. **Idempotency is the Goal**: Check state before making changes

## 🔄 Development Workflow

1. **Crawl**: Build simple, read-only tools
2. **Walk**: Add more complex operations
3. **Run**: Use existing tools to build new tools (recursive improvement)

## 🤝 Contributing

This is a personal project, but feel free to fork and adapt for your own infrastructure!

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

Built by [@scatat](https://github.com/scatat) - A platform engineer learning Python through practical AI tooling.
