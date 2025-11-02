# Platform MCP Server

A personal Model Context Protocol (MCP) server that wraps platform engineering tools (Ansible, Kubernetes, Flux, Git) into secure, idempotent commands for AI agents.

> **Note**: This MCP server is designed to be managed by Ansible as part of the [`ansible-mac`](https://github.com/scatat/ansible-mac) infrastructure automation. Manual installation is possible but not recommended.

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

## 🚀 Installation

### Recommended: Ansible-Managed Installation

This MCP server is automatically installed and configured by the `ansible-mac` playbook:

```bash
# Clone the ansible-mac repository
git clone https://github.com/scatat/ansible-mac.git
cd ansible-mac

# Install all MCP servers (including platform-tools)
ansible-playbook playbooks/zed-mcp.yml

# Or install just this MCP server
ansible-playbook playbooks/zed-mcp.yml --tags platform-tools
```

**What Ansible Does**:
1. Clones this repository to `~/src/mcp-servers/platform-mcp-server`
2. Creates Python virtual environment with `uv`
3. Installs dependencies from `requirements.txt`
4. Configures Zed editor's `settings.json` with correct paths
5. Ensures PATH is set for kubectl, ansible, etc.

### Manual Installation (Not Recommended)

If you must install manually:

```bash
# Clone the repository
git clone https://github.com/scatat/platform-mcp-server.git
cd platform-mcp-server

# Create virtual environment with uv
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Test the server
python platform_mcp.py
```

Then manually configure your MCP client (Zed, Claude Desktop, etc.) - see `TESTING.md`.

## 📚 Available Tools

### V0: Meta-Workflow Discovery (Self-Documentation)

| Tool | Description | Status |
|------|-------------|--------|
| `list_meta_workflows` | List available meta-workflows from META-WORKFLOWS.md | ✅ Implemented |
| `workflow://meta-workflows` | MCP Resource: Read META-WORKFLOWS.md content | ✅ Implemented |

**What are Meta-Workflows?**

Meta-workflows are documented, repeatable processes for common platform engineering tasks. They solve the "chicken-and-egg" problem where the AI doesn't know these processes exist unless explicitly told.

**How It Works:**

1. **Discovery Tool** (`list_meta_workflows`): Returns a structured list of available workflows with their trigger phrases
2. **Resource** (`workflow://meta-workflows`): Exposes the full META-WORKFLOWS.md file as readable context

**Example Usage:**

```python
# AI can call this automatically
result = list_meta_workflows()
# Returns: 7 workflows including "Thread Ending Summary", "New MCP Tool Development", etc.

# Or read the full document
content = read_resource("workflow://meta-workflows")
# Returns: Full META-WORKFLOWS.md content
```

**Why This Matters:**

Without these tools, you'd need to manually tell the AI about workflows in every new session. With them, the AI can discover available processes automatically, making the system self-documenting.

See [META-WORKFLOWS.md](META-WORKFLOWS.md) for all available workflows.

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

## 📖 Core Principles

1. **Clarity over Cuteness**: Simple, readable Python with analogies
2. **Security is Non-Negotiable**: No shortcuts on input validation
3. **Docstrings & Type Hints are our API**: The AI reads these to understand tools
4. **Idempotency is the Goal**: Check state before making changes

## 🔄 Development Workflow

1. **Crawl**: Build simple, read-only tools
2. **Walk**: Add more complex operations
3. **Run**: Use existing tools to build new tools (recursive improvement)

## 🧪 Testing

### If Installed via Ansible

```bash
# Test the MCP dependencies layer
ansible-playbook ~/personal/git/ansible-mac/playbooks/test-mcp-dependencies.yml

# Test the Zed configuration
ansible-playbook ~/personal/git/ansible-mac/playbooks/test-zed-mcp.yml --tags platform-tools

# Verify in Zed
# 1. Restart Zed
# 2. Open Agent panel (Cmd+Shift+A)
# 3. Look for "platform-tools" in context servers
# 4. Try: "List my Kubernetes contexts"
```

### Manual Testing

```bash
# Test the tool directly
cd ~/src/mcp-servers/platform-mcp-server
source .venv/bin/activate
python test_server.py

# Expected output:
# ✅ MCP Server module loaded successfully!
# 🧪 Testing list_kube_contexts tool directly...
# ✅ Success! Found 3 Kubernetes context(s):
#   - bzero-root@home
#   - default
#   - k3s-ansible
```

See `TESTING.md` for comprehensive testing guide.

## 📁 File Locations (Ansible-Managed)

```
~/src/mcp-servers/platform-mcp-server/  # Repository root
├── platform_mcp.py                      # Main MCP server
├── .venv/                               # Python virtual environment (uv)
│   └── bin/python                       # Python interpreter
├── requirements.txt                     # Python dependencies
├── test_server.py                       # Local test script
├── README.md                            # This file
└── TESTING.md                           # Testing guide

~/.config/zed/settings.json              # Zed configuration (managed by Ansible)
```

## 🎛️ Configuration

When managed by Ansible, configuration is in `ansible-mac/roles/zed-mcp/defaults/main.yml`:

```yaml
# Enable/disable the platform-tools MCP
zed_mcp_platform_tools_enabled: true

# Repository and paths (usually don't need to change)
zed_mcp_platform_tools_repo: "https://github.com/scatat/platform-mcp-server.git"
zed_mcp_platform_tools_dest: "{{ zed_mcp_src_dir }}/platform-mcp-server"
zed_mcp_platform_tools_version: "main"
```

## 🐛 Troubleshooting

### MCP Server Not Loading in Zed

```bash
# Check if dependencies were installed
ls -la ~/src/mcp-servers/platform-mcp-server/.venv/

# Re-run MCP dependencies installation
ansible-playbook ~/personal/git/ansible-mac/playbooks/zed-mcp.yml --tags mcp-dependencies

# Re-run Zed configuration
ansible-playbook ~/personal/git/ansible-mac/playbooks/zed-mcp.yml --tags platform-tools

# Restart Zed editor
```

### Tool Returns "kubectl not found"

```bash
# Check PATH is configured in Zed settings
cat ~/.config/zed/settings.json | grep -A 3 "platform-tools"

# Should show:
# "env": {
#   "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
# }
```

### Python Module Errors

```bash
# Reinstall dependencies
cd ~/src/mcp-servers/platform-mcp-server
source .venv/bin/activate
uv pip install -r requirements.txt

# Or use Ansible to fix
ansible-playbook ~/personal/git/ansible-mac/playbooks/zed-mcp.yml --tags mcp-dependencies,platform-tools
```

## 🤝 Contributing

This is a personal project, but feel free to fork and adapt for your own infrastructure!

**Development Workflow**:
1. Make changes to `platform_mcp.py`
2. Test locally with `python test_server.py`
3. Commit and push to GitHub
4. Run `ansible-playbook ~/personal/git/ansible-mac/playbooks/zed-mcp.yml --tags mcp-dependencies,platform-tools`
5. Restart Zed and test

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

Built by [@scatat](https://github.com/scatat) - A platform engineer learning Python through practical AI tooling.

## 🔗 Related Projects

- [ansible-mac](https://github.com/scatat/ansible-mac) - Ansible automation for macOS (manages this MCP server)
- [mcp-sysoperator](https://github.com/tarnover/mcp-sysoperator) - Ansible/AWS/Terraform MCP tools
- [FastMCP](https://github.com/jlowin/fastmcp) - Python framework for building MCP servers

---

**🎯 Quick Start**: Use [`ansible-mac`](https://github.com/scatat/ansible-mac) to install and configure this MCP server automatically.