#!/usr/bin/env python3
"""
Platform MCP Server - Main Entry Point (V2.0)

This is the main entry point for the Platform MCP Server, now reorganized
using the 3-layer architecture model.

ARCHITECTURE:
- src/layers/platform.py: Universal infrastructure primitives (Teleport, SSH)
- src/layers/team.py: Team-specific patterns (Flux, K8s access)
- src/layers/personal.py: Individual workflows (session mgmt, validation)

This file:
1. Imports all tools from the layer modules
2. Registers them with a single MCP server instance
3. Defines MCP resources (documentation, patterns, etc.)
4. Starts the MCP server

ANALOGY: This is like a main() function that orchestrates all the modules.

VERSION: 2.0.0 (Layer Architecture)
"""

# =============================================================================
# IMPORTS
# =============================================================================

import importlib
import json
from pathlib import Path

import yaml
from mcp.server.fastmcp import FastMCP

# Import layer modules
# Note: These contain plain functions, not decorated tools yet
from src.layers import personal, platform

# =============================================================================
# CONFIG LOADING
# =============================================================================


def load_team_config():
    """Load team configuration from team-config.yaml"""
    config_path = Path(__file__).parent / "team-config.yaml"

    if not config_path.exists():
        # Default config if file doesn't exist
        return {
            "team_name": "platform-integrations",
            "team_layer_module": "src.layers.team",
            "team_description": "Platform Integrations - Connects Wise to payment schemes and 3rd parties",
        }

    with open(config_path) as f:
        return yaml.safe_load(f)


# Load config and dynamically import team layer
config = load_team_config()
team_module_path = config.get("team_layer_module", "src.layers.team")
team = importlib.import_module(team_module_path)

# =============================================================================
# SERVER INITIALIZATION
# =============================================================================

# Create main MCP server instance
# All tools from all layers will be registered with this single instance
mcp = FastMCP("platform-tools")

# =============================================================================
# LAYER 1: PLATFORM TOOLS (Universal Infrastructure)
# =============================================================================
# These tools work for ANYONE in the organization.
# No team-specific assumptions.


@mcp.tool()
def check_tsh_installed():
    """Check if Teleport CLI (tsh) is installed and accessible."""
    return platform.check_tsh_installed()


@mcp.tool()
def get_tsh_client_version():
    """Get the installed Teleport CLI (tsh) client version."""
    return platform.get_tsh_client_version()


@mcp.tool()
def get_teleport_proxy_version(cluster: str):
    """Get the Teleport proxy (server) version for a specific cluster."""
    return platform.get_teleport_proxy_version(cluster)


@mcp.tool()
def verify_teleport_compatibility():
    """Complete pre-flight check: Verify tsh installation and compatibility."""
    return platform.verify_teleport_compatibility()


@mcp.tool()
def list_teleport_nodes(cluster: str, filter: str = None):
    """List available SSH nodes in a Teleport cluster."""
    return platform.list_teleport_nodes(cluster, filter)


@mcp.tool()
def verify_ssh_access(cluster: str, node: str, user: str = "root"):
    """Verify you can SSH to a specific node via Teleport."""
    return platform.verify_ssh_access(cluster, node, user)


@mcp.tool()
def run_remote_command(
    cluster: str, node: str, command: str, user: str = "root", timeout: int = 30
):
    """Execute a command on a remote node via Teleport SSH."""
    return platform.run_remote_command(cluster, node, command, user, timeout)


@mcp.tool()
def list_kube_contexts():
    """List all available Kubernetes contexts from your kubeconfig."""
    return platform.list_kube_contexts()


# =============================================================================
# LAYER 2: TEAM TOOLS (Team-Specific Patterns)
# =============================================================================
# These tools implement YOUR team's specific infrastructure patterns.
# Other teams might fork and replace this layer with their own.


@mcp.tool()
def list_flux_kustomizations(cluster: str, node: str, show_suspend: bool = False):
    """List Flux Kustomizations on a Kubernetes node."""
    return team.list_flux_kustomizations(cluster, node, show_suspend)


@mcp.tool()
def get_kustomization_details(
    cluster: str, node: str, name: str, namespace: str = "flux-system"
):
    """Get detailed information about a specific Flux Kustomization."""
    return team.get_kustomization_details(cluster, node, name, namespace)


@mcp.tool()
def reconcile_flux_kustomization(
    cluster: str, node: str, name: str, namespace: str = "flux-system"
):
    """Trigger a Flux reconciliation for a specific Kustomization."""
    return team.reconcile_flux_kustomization(cluster, node, name, namespace)


@mcp.tool()
def list_flux_sources(cluster: str, node: str):
    """List all Flux GitRepository sources."""
    return team.list_flux_sources(cluster, node)


@mcp.tool()
def suspend_flux_kustomization(
    cluster: str, node: str, name: str, namespace: str = "flux-system"
):
    """Suspend a Flux Kustomization (pause reconciliation)."""
    return team.suspend_flux_kustomization(cluster, node, name, namespace)


@mcp.tool()
def resume_flux_kustomization(
    cluster: str, node: str, name: str, namespace: str = "flux-system"
):
    """Resume a suspended Flux Kustomization."""
    return team.resume_flux_kustomization(cluster, node, name, namespace)


@mcp.tool()
def get_flux_logs(
    cluster: str, node: str, component: str = "kustomize-controller", tail: int = 50
):
    """Get logs from a Flux component."""
    return team.get_flux_logs(cluster, node, component, tail)


@mcp.tool()
def get_kustomization_events(
    cluster: str, node: str, name: str, namespace: str = "flux-system"
):
    """Get Kubernetes events for a specific Kustomization."""
    return team.get_kustomization_events(cluster, node, name, namespace)


# =============================================================================
# LAYER 3: PERSONAL TOOLS (Individual Workflows)
# =============================================================================
# These tools support individual developer workflows.
# Highly personalized to your specific setup.


@mcp.tool()
def propose_tool_design(
    tool_name: str,
    purpose: str,
    layer: str,
    dependencies: list,
    requires_system_state_change: bool = False,
    implementation_approach: str = "",
):
    """Propose a new tool design and validate it against the design checklist."""
    return personal.propose_tool_design(
        tool_name,
        purpose,
        layer,
        dependencies,
        requires_system_state_change,
        implementation_approach,
    )


@mcp.tool()
def verify_tool_design_token(token: str):
    """Verify a tool design validation token."""
    return personal.verify_tool_design_token(token)


@mcp.tool()
def list_tool_proposals():
    """List all validated tool proposals."""
    return personal.list_tool_proposals()


@mcp.tool()
def create_mcp_tool(
    tool_name: str, tool_code: str, validation_token: str, description: str = ""
):
    """Create a new MCP tool with ENFORCED design validation."""
    return personal.create_mcp_tool(tool_name, tool_code, validation_token, description)


@mcp.tool()
def list_meta_workflows():
    """Get available meta-workflows for platform operations."""
    return personal.list_meta_workflows()


@mcp.tool()
def analyze_critical_path(tasks: list, goal: str = None, current_state: list = None):
    """Analyze task dependencies and determine optimal work order."""
    return personal.analyze_critical_path(tasks, goal, current_state)


@mcp.tool()
def make_roadmap_decision(tasks: list, analysis_token: str, rationale: str = ""):
    """Make a roadmap decision based on critical path analysis."""
    return personal.make_roadmap_decision(tasks, analysis_token, rationale)


@mcp.tool()
def create_session_note(
    content: str, section: str = "Progress", session_name: str = None
):
    """Create or append to current session ephemeral note."""
    return personal.create_session_note(content, section, session_name)


@mcp.tool()
def read_session_notes(session_name: str = None, days_back: int = 7):
    """Read recent session notes from ephemeral directory."""
    return personal.read_session_notes(session_name, days_back)


@mcp.tool()
def list_session_files(days_back: int = 30):
    """List all session files in ephemeral directory with metadata."""
    return personal.list_session_files(days_back)


@mcp.tool()
def test_enforcement_workflow():
    """Test tool to verify enforcement workflows are functional."""
    return personal.test_enforcement_workflow()


# =============================================================================
# MCP RESOURCES: Documentation & Patterns
# =============================================================================
# Resources are "readable documents" that the AI can access for context.
# Think of them like mounted config files in a container.


# =============================================================================
# MCP PROMPTS: Workflow Discovery
# =============================================================================
# Prompts are "shortcuts" that make workflows discoverable via /commands


# =============================================================================
# RESOURCES REGISTRATION
# =============================================================================
# Register MCP resources (documentation, patterns, etc.)
# These must be registered after mcp is created

mcp.resource("workflow://meta-workflows")(personal.get_meta_workflows_resource)
mcp.resource("workflow://patterns/state-management")(
    personal.get_state_management_pattern
)
mcp.resource("workflow://patterns/session-documentation")(
    personal.get_session_documentation_pattern
)
mcp.resource("workflow://architecture/layer-model")(personal.get_layer_model_resource)
mcp.resource("workflow://rules/design-checklist")(personal.get_design_checklist_resource)

mcp.resource("workflow://team/pi/operating-rules")(team.get_pi_team_rules_resource)

mcp.resource("workflow://user/personal-rules")(personal.get_personal_rules_resource)

# =============================================================================
# PROMPTS REGISTRATION
# =============================================================================
# Register MCP prompts (workflow shortcuts)
# These must be registered after mcp is created

mcp.prompt()(personal.new_tool_workflow)
mcp.prompt()(personal.end_session_workflow)
mcp.prompt()(personal.debug_flux_workflow)
mcp.prompt()(personal.validate_design_workflow)

# =============================================================================
# SERVER STARTUP
# =============================================================================

if __name__ == "__main__":
    # Start the MCP server
    # This runs the FastMCP server which listens for requests from the AI
    mcp.run()
