# Team Onboarding Guide - Platform MCP Server

Quick guide for Wise platform teams (Compute, Connect, CI, CD, etc.) to adopt this MCP server.

## What Is This?

An MCP server that wraps platform tools (Teleport, SSH, kubectl, Flux) into AI-accessible commands. Built with 3-layer architecture for easy team customization.

## Prerequisites

- Teleport access to your team's clusters
- SSH access to nodes
- Python 3.11+
- Zed editor (or another MCP client)

## Quick Start

### 1. Fork and Clone

```bash
git clone https://github.com/your-org/platform-mcp-server.git
cd platform-mcp-server
```

### 2. Install Dependencies

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3. Customize for Your Team

**Option A: Use as-is** (if you use Flux + SSH-based K8s access)
- Just update `team-config.yaml` with your team name
- Start using immediately

**Option B: Replace team layer** (if you use different tools)
- Copy `src/layers/team_example.py` to `src/layers/team_yourteam.py`
- Add your team's tools (ArgoCD, different K8s access, etc.)
- Update `team-config.yaml` → `team_layer_module: "src.layers.team_yourteam"`

### 4. Configure Zed

Add to `~/.config/zed/settings.json`:

```json
{
  "context_servers": {
    "your-team-mcp": {
      "command": "/path/to/platform-mcp-server/.venv/bin/python",
      "args": ["/path/to/platform-mcp-server/platform_mcp.py"],
      "env": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

Restart Zed.

## What You Get

**Platform Layer** (works for all Wise teams):
- Teleport authentication
- SSH primitives
- Remote command execution

**Team Layer** (customize for your team):
- Current: Flux GitOps operations
- You can replace with: ArgoCD, Helm, Terraform, etc.

**Personal Layer** (individual preferences):
- Session management
- Tool validation
- Workflow automation

## Example Team Customizations

### Team: Compute (Hypothetical)
**Infrastructure**: Direct K8s API, Helm  
**Team layer**: Replace with Helm operations, pod management

### Team: Connect (Hypothetical)
**Infrastructure**: Service mesh, Istio  
**Team layer**: Replace with Istio config, traffic management

### Team: CI/CD (Hypothetical)
**Infrastructure**: Jenkins, GitHub Actions  
**Team layer**: Replace with pipeline operations, build triggers

## Questions to Answer

Before customizing:

1. **What infrastructure do you manage?** (K8s, VMs, serverless, etc.)
2. **What tools do you use daily?** (kubectl, flux, argocd, terraform, etc.)
3. **How do you access systems?** (SSH, K8s API, cloud APIs, etc.)
4. **What's your most common operations?** (Deploy, rollback, debug, scale, etc.)

These answers determine your team layer tools.

## Getting Help

- **Architecture**: See `ROADMAP.md`
- **Forking**: See `docs/FORKING-GUIDE.md`
- **Design principles**: See `docs/DESIGN-PRINCIPLES.md`
- **Tool development**: Follow `META-WORKFLOWS.md` → MW-002

## Contributing Back

If you build generic tools others could use, consider contributing them to the **Platform layer** (not team layer). Platform tools should work for any Wise team.