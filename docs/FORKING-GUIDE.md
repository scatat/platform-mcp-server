# Forking Guide - Adapting Platform MCP Server for Your Team

This guide shows how to fork this MCP server and adapt it for your team's specific needs.

## Core Concept

The 3-layer architecture makes forking simple:

- **Keep**: Platform layer (universal primitives)
- **Replace**: Team layer (your team's tools)
- **Customize**: Personal layer (individual preferences)

## Quick Start

### 1. Fork the Repository

```bash
# Fork on GitHub, then clone
git clone https://github.com/your-org/platform-mcp-server.git
cd platform-mcp-server
```

### 2. Create Your Team Layer

```bash
# Copy the example team layer as a starting point
cp src/layers/team_example.py src/layers/team_yourteam.py

# Edit and add your team's tools
vim src/layers/team_yourteam.py
```

### 3. Update Configuration

```bash
# Copy example config
cp team-config.example.yaml team-config.yaml

# Edit to point to your team layer
vim team-config.yaml
```

Change these values:

```yaml
team_name: "your-team-name"
team_layer_module: "src.layers.team_yourteam"
team_description: "Your team's actual function"
```

### 4. Test

```bash
# Install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Test your changes
python platform_mcp.py
```

## What to Modify

### ✅ DO Modify

- **Team layer** (`src/layers/team_*.py`) - Replace with your tools
- **Team config** (`team-config.yaml`) - Your team's settings
- **Personal layer** (`src/layers/personal.py`) - Your individual workflows
- **README.md** - Update team-specific documentation

### ⚠️ DON'T Modify (Unless Necessary)

- **Platform layer** (`src/layers/platform.py`) - Universal primitives
- **Main orchestration** (`platform_mcp.py`) - Core MCP registration
- **Architecture docs** (`ROADMAP.md`, `docs/DESIGN-PRINCIPLES.md`)

## Example: Different Team Types

### Team A (Current - Platform Integrations)

**Infrastructure**: SSH-based Kubernetes, Flux GitOps  
**Team layer**: `src.layers.team` (Flux operations)  
**Config**: `team-config.yaml` → `team_name: "platform-integrations"`

### Team B (Hypothetical - App Team)

**Infrastructure**: Direct kube API, ArgoCD  
**Team layer**: `src.layers.team_appteam` (ArgoCD operations)  
**Config**: `team-config.yaml` → `team_name: "app-team"`

## Keeping Up with Upstream

```bash
# Add upstream remote
git remote add upstream https://github.com/original/platform-mcp-server.git

# Update platform layer from upstream
git fetch upstream
git checkout upstream/main -- src/layers/platform.py

# Merge upstream changes (carefully)
git merge upstream/main
```

## Questions Before You Fork

1. **Can you use Platform layer as-is?** (Teleport, SSH primitives)
   - Yes → Just replace Team layer
   - No → You might need a different MCP server

2. **What's your team's infrastructure?** (K8s, VMs, serverless, etc.)
   - This determines what Team layer tools you need

3. **What operations do you do daily?** (Deploy, debug, monitor, etc.)
   - These become your Team layer tools

## Need Help?

- Check `ROADMAP.md` for architecture details
- See `META-WORKFLOWS.md` for development workflows
- Reference `src/layers/team.py` for real-world examples