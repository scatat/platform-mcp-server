#!/usr/bin/env python3
"""
Platform MCP Server - Personal AI Agent Toolset

This is your personal Model Context Protocol (MCP) server. Think of it as a
"custom command library" that your AI agent can safely call.

ANALOGY: If your AI agent is like a junior engineer on your team, this file is
the "runbook" - a collection of approved, documented procedures they can execute.
"""

# =============================================================================
# IMPORTS: Our Dependencies (like sourcing libraries in Bash)
# =============================================================================

import json  # For parsing JSON responses
import os  # For environment variables and path operations
import re  # For regex parsing (version strings, etc.)
import shlex  # For safely parsing command strings (prevents injection!)
import subprocess  # For running shell commands safely (like calling `kubectl`)
from typing import (  # Type hints - tells us what data type to expect
    Any,
    Dict,
    List,
    Optional,
)

# FastMCP: The MCP server framework (like Flask for APIs, but for AI tools)
from mcp.server.fastmcp import FastMCP

# =============================================================================
# SERVER INITIALIZATION
# =============================================================================

# Create our MCP server instance
# ANALOGY: This is like starting up an HTTP server or SSH daemon
# The "name" is how the AI will identify this server
mcp = FastMCP("platform-tools")


# =============================================================================
# TOOL DEFINITIONS: Our "Safe Commands" for the AI
# =============================================================================


# =============================================================================
# V0: Meta-Workflow Discovery Tools
# =============================================================================
# These tools expose META-WORKFLOWS.md to the AI, solving the "chicken-and-egg"
# problem where the AI doesn't know workflows exist unless explicitly told.
#
# Philosophy: "Self-documenting system" - the MCP server exposes its own
# documentation and processes, making them automatically discoverable.


@mcp.tool()
def list_meta_workflows() -> Dict[str, Any]:
    """
    Get available meta-workflows for platform operations.

    Meta-workflows are documented, repeatable processes for common platform
    engineering tasks. This tool makes them automatically discoverable.

    ANALOGY: Like running 'man -k workflow' to see available documented processes.

    Returns:
        dict: Available workflows with triggers and descriptions
        {
            "available": bool,
            "count": int,
            "workflows": [
                {
                    "id": str,          # e.g., "MW-001"
                    "name": str,        # e.g., "Thread Ending Summary"
                    "trigger": str,     # e.g., "This thread is ending"
                    "status": str       # "active" or "draft"
                },
                ...
            ],
            "message": str,
            "full_doc_path": str        # Path to META-WORKFLOWS.md
        }

    Example Response:
        {
            "available": true,
            "count": 8,
            "workflows": [
                {
                    "id": "MW-001",
                    "name": "Thread Ending Summary",
                    "trigger": "This thread is ending",
                    "status": "active"
                },
                ...
            ],
            "message": "✅ Found 8 meta-workflows (6 active, 2 draft)",
            "full_doc_path": "META-WORKFLOWS.md"
        }

    SECURITY NOTES:
    - Read-only operation (just reads META-WORKFLOWS.md)
    - No user input accepted
    - File path is hardcoded (no path traversal risk)

    HOW TO USE:
    - Call this at the start of complex operations
    - If a workflow exists for your task, use it
    - Workflows provide step-by-step guidance with validation
    """

    # Find META-WORKFLOWS.md relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workflows_path = os.path.join(script_dir, "META-WORKFLOWS.md")

    # Check if file exists
    if not os.path.exists(workflows_path):
        return {
            "available": False,
            "count": 0,
            "workflows": [],
            "message": "❌ META-WORKFLOWS.md not found",
            "full_doc_path": None,
            "ansible_command": None,
            "ansible_steps": [
                "File should exist at: " + workflows_path,
                "Check if platform-mcp-server repository is complete",
            ],
        }

    # Read the file
    try:
        with open(workflows_path, "r") as f:
            content = f.read()
    except Exception as e:
        return {
            "available": False,
            "count": 0,
            "workflows": [],
            "message": f"❌ Error reading META-WORKFLOWS.md: {str(e)}",
            "full_doc_path": workflows_path,
        }

    # Parse workflow registry from the content
    # Look for the Active Workflows table
    workflows = []

    # Simple regex to extract workflow info from the markdown table
    # Format: | MW-001 | Thread Ending Summary | "This thread is ending" | Active | 2024-11-02 |
    import re

    table_pattern = r'\|\s*(MW-\d+)\s*\|\s*([^|]+)\|\s*"([^"]+)"\s*\|\s*(\w+)\s*\|'

    for match in re.finditer(table_pattern, content):
        workflow_id = match.group(1).strip()
        name = match.group(2).strip()
        trigger = match.group(3).strip()
        status = match.group(4).strip().lower()

        workflows.append(
            {"id": workflow_id, "name": name, "trigger": trigger, "status": status}
        )

    # Count active vs draft
    active_count = sum(1 for w in workflows if w["status"] == "active")
    draft_count = sum(1 for w in workflows if w["status"] == "draft")

    if not workflows:
        return {
            "available": True,
            "count": 0,
            "workflows": [],
            "message": "⚠️  META-WORKFLOWS.md exists but no workflows found in registry",
            "full_doc_path": "META-WORKFLOWS.md",
        }

    return {
        "available": True,
        "count": len(workflows),
        "workflows": workflows,
        "message": f"✅ Found {len(workflows)} meta-workflow(s) ({active_count} active, {draft_count} draft)",
        "full_doc_path": "META-WORKFLOWS.md",
        "ansible_command": None,
        "ansible_steps": [
            "To see full workflow details, read META-WORKFLOWS.md",
            f"To execute a workflow, use its trigger phrase (e.g., '{workflows[0]['trigger']}')",
        ],
    }


@mcp.resource("workflow://meta-workflows")
def get_meta_workflows_resource() -> str:
    """
    MCP Resource: META-WORKFLOWS.md content.

    This exposes META-WORKFLOWS.md as a readable resource via the MCP protocol.
    Resources are like "context files" that the AI can access for reference.

    ANALOGY: Like a shared documentation folder mounted in a container.

    Returns:
        str: Full content of META-WORKFLOWS.md

    SECURITY NOTES:
    - Read-only access
    - File path is hardcoded (no path traversal)
    - No user input accepted
    """

    # Find META-WORKFLOWS.md relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workflows_path = os.path.join(script_dir, "META-WORKFLOWS.md")

    # Check if file exists
    if not os.path.exists(workflows_path):
        return "❌ META-WORKFLOWS.md not found at: " + workflows_path

    # Read and return content
    try:
        with open(workflows_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"❌ Error reading META-WORKFLOWS.md: {str(e)}"


@mcp.resource("workflow://patterns/state-management")
def get_state_management_pattern() -> str:
    """
    MCP Resource: State Management Pattern (transient vs persistent state).

    This exposes the state management pattern as a structured YAML resource.
    Defines the .ephemeral/ vs docs/sessions/ separation.

    ANALOGY: Like a configuration schema that explains how to organize files.

    Returns:
        str: Full content of resources/patterns/state-management.yaml

    SECURITY NOTES:
    - Read-only access
    - File path is hardcoded (no path traversal)
    - No user input accepted
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))
    pattern_path = os.path.join(script_dir, "resources/patterns/state-management.yaml")

    if not os.path.exists(pattern_path):
        return "❌ state-management.yaml not found at: " + pattern_path

    try:
        with open(pattern_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"❌ Error reading state-management.yaml: {str(e)}"


@mcp.resource("workflow://patterns/session-documentation")
def get_session_documentation_pattern() -> str:
    """
    MCP Resource: Session Documentation Pattern (FINAL-SUMMARY.md template).

    This exposes the session documentation pattern as a structured YAML resource.
    Defines the template and rules for creating session summaries.

    ANALOGY: Like a template file that shows the format for documentation.

    Returns:
        str: Full content of resources/patterns/session-documentation.yaml

    SECURITY NOTES:
    - Read-only access
    - File path is hardcoded (no path traversal)
    - No user input accepted
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))
    pattern_path = os.path.join(
        script_dir, "resources/patterns/session-documentation.yaml"
    )

    if not os.path.exists(pattern_path):
        return "❌ session-documentation.yaml not found at: " + pattern_path

    try:
        with open(pattern_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"❌ Error reading session-documentation.yaml: {str(e)}"


@mcp.resource("workflow://architecture/layer-model")
def get_layer_model_resource() -> str:
    """
    MCP Resource: 3-Layer Architecture Model (Platform/Team/Personal).

    This exposes the layer model as a structured YAML resource.
    Defines the architectural boundaries for multi-team adoption.

    ANALOGY: Like an architecture diagram as data.

    Returns:
        str: Full content of resources/architecture/layer-model.yaml

    SECURITY NOTES:
    - Read-only access
    - File path is hardcoded (no path traversal)
    - No user input accepted
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "resources/architecture/layer-model.yaml")

    if not os.path.exists(model_path):
        return "❌ layer-model.yaml not found at: " + model_path

    try:
        with open(model_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"❌ Error reading layer-model.yaml: {str(e)}"


@mcp.resource("workflow://rules/design-checklist")
def get_design_checklist_resource() -> str:
    """
    MCP Resource: Design Checklist (Structured rules for MCP tool development).

    This exposes the design checklist as a structured YAML resource.
    Defines actionable rules, red flags, and validation criteria for new tools.

    ANALOGY: Like a linter configuration that defines code quality rules.

    Returns:
        str: Full content of resources/rules/design-checklist.yaml

    SECURITY NOTES:
    - Read-only access
    - File path is hardcoded (no path traversal)
    - No user input accepted
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))
    checklist_path = os.path.join(script_dir, "resources/rules/design-checklist.yaml")

    if not os.path.exists(checklist_path):
        return "❌ design-checklist.yaml not found at: " + checklist_path

    try:
        with open(checklist_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"❌ Error reading design-checklist.yaml: {str(e)}"


# =============================================================================
# V1a: Kubernetes Context Discovery
# =============================================================================


@mcp.tool()
def list_kube_contexts() -> str:
    """
    List all available Kubernetes contexts from your kubeconfig.

    This is a READ-ONLY tool. It doesn't change anything, just shows info.
    Think of it like running `ls` - it's safe because it only looks, never touches.

    Returns:
        str: A newline-separated list of context names (e.g., "prod\\nstaging\\ndev")

    Example Output:
        homelab-admin@homelab
        docker-desktop
        kind-local

    SECURITY NOTES:
    - No user input is accepted (no injection risk)
    - Uses shell=False (prevents command injection)
    - Read-only operation (can't break anything)
    """

    # STEP 1: Define the command as a list
    # ANALOGY: This is like writing each argument on a separate line in a script
    # We do this instead of a string to prevent shell injection attacks
    # BAD:  "kubectl config get-contexts -o name"  <- could be manipulated
    # GOOD: ["kubectl", "config", "get-contexts", "-o", "name"]  <- safe!
    command = ["kubectl", "config", "get-contexts", "-o", "name"]

    try:
        # STEP 2: Run the command safely
        # ANALOGY: This is like running a command in a sandbox
        # - shell=False: Don't use the shell (prevents injection)
        # - capture_output=True: Grab the output so we can return it
        # - text=True: Treat output as text (not raw bytes)
        # - check=True: Raise an error if command fails (like `set -e` in Bash)
        result = subprocess.run(
            command,
            shell=False,  # CRITICAL: Never use shell=True with user input!
            capture_output=True,  # Capture stdout and stderr
            text=True,  # Return strings, not bytes
            check=True,  # Raise exception if command fails
        )

        # STEP 3: Return the output
        # .strip() removes leading/trailing whitespace (like `trim()`)
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        # STEP 4: Handle errors gracefully
        # ANALOGY: This is like `trap` in Bash - catch errors and report them nicely
        # The AI will see this error message and can tell the user what went wrong
        return f"Error running kubectl: {e.stderr}"

    except FileNotFoundError:
        # STEP 5: Handle missing commands
        # If kubectl isn't installed, tell the AI clearly
        return "Error: kubectl command not found. Is kubectl installed and in PATH?"


# =============================================================================
# CONSTANTS: Configuration Values
# =============================================================================

# Ansible-mac repository path
# ANALOGY: This is like setting a variable at the top of a Bash script
ANSIBLE_MAC_PATH = os.path.expanduser("~/personal/git/ansible-mac")

# Allowed Teleport clusters (security: only these are permitted)
# ANALOGY: Like an allow-list in a firewall rule
# Architecture: 3 environments
#   - "staging": Lower environment for testing
#   - "production": Production workloads
#   - "shared-services": Privileged infrastructure cluster (can access both staging & production)
#                        This is where K8s/Flux infrastructure runs
ALLOWED_TELEPORT_CLUSTERS = ["staging", "production", "shared-service"]

# Expected tsh binary path
TSH_BINARY_PATH = "/usr/local/bin/tsh"


# =============================================================================
# V1a TOOLS: Teleport Discovery & Version Management
# =============================================================================
# These tools check Teleport installation and compatibility BEFORE attempting
# any operations. They provide intelligent guidance on how to fix issues using
# Ansible.
#
# Philosophy: "Check, don't change" - these are read-only discovery tools that
# give the AI (and user) full visibility into the environment state.


@mcp.tool()
def check_tsh_installed() -> Dict[str, Any]:
    """
    Check if Teleport CLI (tsh) is installed and accessible.

    This is a READ-ONLY discovery tool. It checks if tsh exists but doesn't
    install or modify anything.

    ANALOGY: Like checking if a tool exists in /usr/bin before trying to use it.

    Returns:
        dict: Installation status and guidance
        {
            "installed": bool,
            "path": str,              # Path to tsh binary (if found)
            "message": str,           # Human-readable status
            "ansible_command": str,   # Command to fix (if needed)
            "ansible_steps": List[str] # Step-by-step fix instructions
        }

    Example Responses:

        If installed:
        {
            "installed": true,
            "path": "/usr/local/bin/tsh",
            "message": "✅ tsh is installed at /usr/local/bin/tsh",
            "ansible_command": null,
            "ansible_steps": []
        }

        If not installed:
        {
            "installed": false,
            "path": null,
            "message": "❌ tsh is not installed",
            "ansible_command": "ansible-playbook ~/personal/git/ansible-mac/playbooks/teleport.yml",
            "ansible_steps": [
                "cd ~/personal/git/ansible-mac",
                "ansible-playbook playbooks/teleport.yml",
                "Verify: tsh version"
            ]
        }

    SECURITY NOTES:
    - Read-only check (no modifications)
    - No user input accepted
    - Provides Ansible guidance instead of installing directly
    """

    # STEP 1: Check if tsh exists at expected path
    if os.path.isfile(TSH_BINARY_PATH) and os.access(TSH_BINARY_PATH, os.X_OK):
        # tsh exists and is executable
        return {
            "installed": True,
            "path": TSH_BINARY_PATH,
            "message": f"✅ tsh is installed at {TSH_BINARY_PATH}",
            "ansible_command": None,
            "ansible_steps": [],
        }
    else:
        # tsh not found - provide installation guidance
        return {
            "installed": False,
            "path": None,
            "message": "❌ tsh is not installed",
            "ansible_command": f"ansible-playbook {ANSIBLE_MAC_PATH}/playbooks/teleport.yml",
            "ansible_steps": [
                f"cd {ANSIBLE_MAC_PATH}",
                "ansible-playbook playbooks/teleport.yml",
                "Verify: tsh version",
                "",
                "This will install tsh using the version-pinned Ansible role.",
            ],
        }


@mcp.tool()
def get_tsh_client_version() -> Dict[str, Any]:
    """
    Get the installed Teleport CLI (tsh) client version.

    This tool reads the version of the installed tsh binary. It checks if tsh
    is installed first, and provides guidance if not.

    ANALOGY: Like running `tsh version` to see what version you have installed.

    Returns:
        dict: Version information or error with guidance
        {
            "success": bool,
            "version": str,           # e.g., "16.4.8"
            "full_version": str,      # e.g., "Teleport v16.4.8 git:..."
            "message": str,
            "ansible_command": str,   # If installation needed
            "ansible_steps": List[str]
        }

    Example Responses:

        If installed:
        {
            "success": true,
            "version": "17.7.1",
            "full_version": "Teleport v17.7.1 git:v17.7.1-0-g...",
            "message": "✅ tsh client version: 17.7.1",
            "ansible_command": null,
            "ansible_steps": []
        }

        If not installed:
        {
            "success": false,
            "version": null,
            "message": "❌ tsh is not installed",
            "ansible_command": "ansible-playbook ~/personal/git/ansible-mac/playbooks/teleport.yml",
            "ansible_steps": [...]
        }

    SECURITY NOTES:
    - Read-only operation
    - Uses check_tsh_installed() first (defensive programming)
    - No shell=True (prevents injection)
    """

    # STEP 1: Verify tsh is installed (defensive programming)
    install_check = check_tsh_installed()
    if not install_check["installed"]:
        return {
            "success": False,
            "version": None,
            "full_version": None,
            "message": install_check["message"],
            "ansible_command": install_check["ansible_command"],
            "ansible_steps": install_check["ansible_steps"],
        }

    # STEP 2: Get version from tsh
    command = [TSH_BINARY_PATH, "version"]

    try:
        result = subprocess.run(
            command,
            shell=False,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )

        full_version = result.stdout.strip()

        # STEP 3: Parse version number
        # Example output: "Teleport v16.4.8 git:v16.4.8-0-g..."
        # We want to extract: "16.4.8"
        version_match = re.search(r"v(\d+\.\d+\.\d+)", full_version)

        if version_match:
            version = version_match.group(1)
            return {
                "success": True,
                "version": version,
                "full_version": full_version,
                "message": f"✅ tsh client version: {version}",
                "ansible_command": None,
                "ansible_steps": [],
            }
        else:
            return {
                "success": False,
                "version": None,
                "full_version": full_version,
                "message": f"⚠️  Could not parse version from: {full_version}",
                "ansible_command": None,
                "ansible_steps": ["Run 'tsh version' manually to check output format"],
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "version": None,
            "full_version": None,
            "message": "❌ tsh version command timed out",
            "ansible_command": None,
            "ansible_steps": ["Check if tsh is responsive"],
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "version": None,
            "full_version": None,
            "message": f"❌ Error getting tsh version: {e.stderr}",
            "ansible_command": None,
            "ansible_steps": ["Run 'tsh version' manually to debug"],
        }
    except Exception as e:
        return {
            "success": False,
            "version": None,
            "full_version": None,
            "message": f"❌ Unexpected error: {str(e)}",
            "ansible_command": None,
            "ansible_steps": ["Run 'tsh version' manually to debug"],
        }


@mcp.tool()
def get_teleport_proxy_version(cluster: str) -> Dict[str, Any]:
    """
    Get the Teleport proxy (server) version for a specific cluster.

    This tool connects to a Teleport cluster and checks what version the proxy
    server is running. This is needed to verify client/server compatibility.

    IMPORTANT: Teleport has backwards compatibility (old client works with new
    server) but NOT forward compatibility (new client may fail with old server).

    ANALOGY: Like pinging a server to check its version before connecting.

    Args:
        cluster: Must be one of ["staging", "production"]

    Returns:
        dict: Proxy version information or error with guidance
        {
            "success": bool,
            "cluster": str,
            "proxy_version": str,     # e.g., "17.7.1"
            "proxy_url": str,         # e.g., "teleport.tw.ee:443"
            "client_version": str,
            "compatible": bool,       # True if client <= server
            "message": str,
            "ansible_command": str,
            "ansible_steps": List[str]
        }

    Example Responses:

        Compatible:
        {
            "success": true,
            "cluster": "staging",
            "proxy_version": "17.7.1",
            "proxy_url": "teleport.tw.ee:443",
            "client_version": "17.7.1",
            "compatible": true,
            "message": "✅ Client (17.7.1) is compatible with staging proxy (17.7.1)"
        }

        Version mismatch:
        {
            "success": true,
            "cluster": "production",
            "proxy_version": "17.7.1",
            "client_version": "16.4.8",
            "compatible": true,  # Backwards compatible
            "message": "⚠️  Client (16.4.8) is older than production proxy (17.7.1). Works due to backwards compatibility, but consider upgrading.",
            "ansible_command": "ansible-playbook ~/personal/git/ansible-mac/playbooks/teleport.yml -e 'teleport_version=17.7.1'",
            "ansible_steps": [...]
        }

    SECURITY NOTES:
    - Input validation: cluster must be in allow-list
    - Read-only operation (just checks version)
    - Checks tsh installation first
    """

    # STEP 1: Validate input
    if cluster not in ALLOWED_TELEPORT_CLUSTERS:
        return {
            "success": False,
            "cluster": cluster,
            "proxy_version": None,
            "proxy_url": None,
            "client_version": None,
            "compatible": False,
            "message": f"❌ Invalid cluster. Must be one of: {ALLOWED_TELEPORT_CLUSTERS}",
            "ansible_command": None,
            "ansible_steps": [],
        }

    # STEP 2: Check if tsh is installed
    install_check = check_tsh_installed()
    if not install_check["installed"]:
        return {
            "success": False,
            "cluster": cluster,
            "proxy_version": None,
            "proxy_url": None,
            "client_version": None,
            "compatible": False,
            "message": "❌ tsh is not installed",
            "ansible_command": install_check["ansible_command"],
            "ansible_steps": install_check["ansible_steps"],
        }

    # STEP 3: Get client version
    client_info = get_tsh_client_version()
    if not client_info["success"]:
        return {
            "success": False,
            "cluster": cluster,
            "proxy_version": None,
            "proxy_url": None,
            "client_version": None,
            "compatible": False,
            "message": f"❌ Cannot determine client version: {client_info['message']}",
            "ansible_command": client_info.get("ansible_command"),
            "ansible_steps": client_info.get("ansible_steps", []),
        }

    client_version = client_info["version"]

    # STEP 4: Ping the proxy to get server version
    # We use: tsh ping --proxy=teleport.tw.ee:443
    proxy_url = "teleport.tw.ee:443"
    command = [TSH_BINARY_PATH, "ping", f"--proxy={proxy_url}"]

    try:
        result = subprocess.run(
            command,
            shell=False,
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Parse output for version
        # Example: "Proxy version: v17.7.1"
        proxy_version = None
        for line in result.stdout.split("\n"):
            if "proxy version" in line.lower():
                version_match = re.search(r"v?(\d+\.\d+\.\d+)", line)
                if version_match:
                    proxy_version = version_match.group(1)
                    break

        if not proxy_version:
            return {
                "success": False,
                "cluster": cluster,
                "proxy_version": None,
                "proxy_url": proxy_url,
                "client_version": client_version,
                "compatible": False,
                "message": f"⚠️  Could not determine proxy version for {cluster}",
                "ansible_command": None,
                "ansible_steps": [
                    f"Run 'tsh ping --proxy={proxy_url}' manually to debug"
                ],
            }

        # STEP 5: Compare versions
        # Helper function to parse version tuples
        def version_tuple(v):
            return tuple(map(int, v.split(".")))

        client_ver_tuple = version_tuple(client_version)
        proxy_ver_tuple = version_tuple(proxy_version)

        # Teleport is backwards compatible (old client, new server = OK)
        # But NOT forwards compatible (new client, old server = BAD)
        compatible = client_ver_tuple <= proxy_ver_tuple

        # STEP 6: Build response with appropriate message
        if client_ver_tuple == proxy_ver_tuple:
            message = f"✅ Client ({client_version}) is compatible with {cluster} proxy ({proxy_version})"
            ansible_command = None
            ansible_steps = []
        elif client_ver_tuple < proxy_ver_tuple:
            message = f"⚠️  Client ({client_version}) is older than {cluster} proxy ({proxy_version}). Works due to backwards compatibility, but consider upgrading."
            ansible_command = f"ansible-playbook {ANSIBLE_MAC_PATH}/playbooks/teleport.yml -e 'teleport_version={proxy_version}'"
            ansible_steps = [
                f"cd {ANSIBLE_MAC_PATH}",
                f"Edit roles/teleport/defaults/main.yml",
                f"Update: teleport_version: '{proxy_version}'",
                "ansible-playbook playbooks/teleport.yml",
                "Verify: tsh version",
            ]
        else:
            message = f"❌ Client ({client_version}) is NEWER than {cluster} proxy ({proxy_version}). This may cause compatibility issues!"
            ansible_command = f"ansible-playbook {ANSIBLE_MAC_PATH}/playbooks/teleport.yml -e 'teleport_version={proxy_version}'"
            ansible_steps = [
                f"cd {ANSIBLE_MAC_PATH}",
                f"Edit roles/teleport/defaults/main.yml",
                f"Update: teleport_version: '{proxy_version}'",
                "ansible-playbook playbooks/teleport.yml",
                "Verify: tsh version",
                "",
                "Note: Downgrading to match server version for compatibility",
            ]

        return {
            "success": True,
            "cluster": cluster,
            "proxy_version": proxy_version,
            "proxy_url": proxy_url,
            "client_version": client_version,
            "compatible": compatible,
            "message": message,
            "ansible_command": ansible_command,
            "ansible_steps": ansible_steps,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "cluster": cluster,
            "proxy_version": None,
            "proxy_url": proxy_url,
            "client_version": client_version,
            "compatible": False,
            "message": f"❌ Timeout connecting to {cluster} proxy at {proxy_url}",
            "ansible_command": None,
            "ansible_steps": [
                "Check network connectivity",
                f"Try: tsh ping --proxy={proxy_url}",
            ],
        }
    except Exception as e:
        return {
            "success": False,
            "cluster": cluster,
            "proxy_version": None,
            "proxy_url": proxy_url,
            "client_version": client_version,
            "compatible": False,
            "message": f"❌ Error checking proxy version: {str(e)}",
            "ansible_command": None,
            "ansible_steps": [f"Run 'tsh ping --proxy={proxy_url}' manually to debug"],
        }


@mcp.tool()
def verify_teleport_compatibility() -> Dict[str, Any]:
    """
    Complete pre-flight check: Verify tsh installation and compatibility with all clusters.

    This is the "smart" tool that orchestrates all the other checks and provides
    a comprehensive status report with actionable guidance.

    ANALOGY: Like running a pre-deployment checklist that checks all dependencies
    and tells you exactly what to fix if something is wrong.

    Uses:
        - check_tsh_installed()
        - get_tsh_client_version()
        - get_teleport_proxy_version("staging")
        - get_teleport_proxy_version("production")

    Returns:
        dict: Complete compatibility report with guidance
        {
            "compatible": bool,           # Overall status
            "tsh_installed": bool,
            "client_version": str,
            "clusters": {
                "staging": {...},
                "production": {...}
            },
            "issues": List[str],          # List of problems found
            "recommendation": str,        # What to do next
            "ansible_command": str,       # Command to fix issues
            "ansible_steps": List[str]    # Step-by-step instructions
        }

    Example Response (All Good):
        {
            "compatible": true,
            "tsh_installed": true,
            "client_version": "17.7.1",
            "clusters": {
                "staging": {"compatible": true, "proxy_version": "17.7.1"},
                "production": {"compatible": true, "proxy_version": "17.7.1"}
            },
            "issues": [],
            "recommendation": "✅ All systems compatible. Ready to run Flux commands on any cluster.",
            "ansible_command": null,
            "ansible_steps": []
        }

    Example Response (Needs Action):
        {
            "compatible": false,
            "tsh_installed": false,
            "issues": ["tsh is not installed"],
            "recommendation": "Install Teleport CLI using Ansible",
            "ansible_command": "ansible-playbook ~/personal/git/ansible-mac/playbooks/teleport.yml",
            "ansible_steps": [...]
        }

    SECURITY NOTES:
    - Read-only operation (just checks, doesn't change anything)
    - Composing multiple safe tools together
    - Provides actionable guidance without executing changes
    """

    # STEP 1: Check if tsh is installed
    install_check = check_tsh_installed()

    if not install_check["installed"]:
        # tsh not installed - can't proceed with other checks
        return {
            "compatible": False,
            "tsh_installed": False,
            "client_version": None,
            "clusters": {},
            "issues": ["tsh is not installed"],
            "recommendation": "Install Teleport CLI (tsh) using Ansible before proceeding",
            "ansible_command": install_check["ansible_command"],
            "ansible_steps": install_check["ansible_steps"],
        }

    # STEP 2: Get client version
    client_info = get_tsh_client_version()
    if not client_info["success"]:
        return {
            "compatible": False,
            "tsh_installed": True,
            "client_version": None,
            "clusters": {},
            "issues": [client_info["message"]],
            "recommendation": "Fix tsh client issues before checking cluster compatibility",
            "ansible_command": client_info.get("ansible_command"),
            "ansible_steps": client_info.get("ansible_steps", []),
        }

    client_version = client_info["version"]

    # STEP 3: Check compatibility with all clusters
    clusters_status = {}
    issues = []
    all_compatible = True
    needs_upgrade_to = None

    for cluster_name in ALLOWED_TELEPORT_CLUSTERS:
        cluster_check = get_teleport_proxy_version(cluster_name)
        clusters_status[cluster_name] = cluster_check

        if not cluster_check["success"]:
            issues.append(f"{cluster_name}: {cluster_check['message']}")
            all_compatible = False
        elif not cluster_check["compatible"]:
            issues.append(cluster_check["message"])
            all_compatible = False
            # Track highest version we need to upgrade to
            if cluster_check["proxy_version"]:
                if (
                    not needs_upgrade_to
                    or cluster_check["proxy_version"] > needs_upgrade_to
                ):
                    needs_upgrade_to = cluster_check["proxy_version"]

    # STEP 4: Build recommendation based on findings
    if all_compatible and not issues:
        recommendation = f"✅ All systems compatible. tsh v{client_version} works with all clusters. Ready to run Flux commands."
        ansible_command = None
        ansible_steps = []
    elif needs_upgrade_to:
        recommendation = f"⚠️  Upgrade tsh to v{needs_upgrade_to} for full compatibility with all clusters."
        ansible_command = f"ansible-playbook {ANSIBLE_MAC_PATH}/playbooks/teleport.yml -e 'teleport_version={needs_upgrade_to}'"
        ansible_steps = [
            f"cd {ANSIBLE_MAC_PATH}",
            f"Edit roles/teleport/defaults/main.yml",
            f"Update: teleport_version: '{needs_upgrade_to}'",
            "ansible-playbook playbooks/teleport.yml",
            "Verify: tsh version",
        ]
    else:
        recommendation = "❌ Multiple issues detected. Review cluster statuses above."
        ansible_command = None
        ansible_steps = ["Review individual cluster compatibility checks above"]

    return {
        "compatible": all_compatible,
        "tsh_installed": True,
        "client_version": client_version,
        "clusters": clusters_status,
        "issues": issues,
        "recommendation": recommendation,
        "ansible_command": ansible_command,
        "ansible_steps": ansible_steps,
    }


# =============================================================================
# V1b TOOLS: Teleport SSH & Remote Command Execution
# =============================================================================
# These tools enable SSH-based remote command execution on instances via Teleport.
# This is the REAL platform engineering workflow - not kube proxy, but SSH to nodes.
#
# Philosophy: "Primitive building blocks + composition"
# - Low-level: run_remote_command() - the primitive
# - High-level: list_flux_kustomizations() - uses the primitive
#
# This architecture works for ANY remote command on ANY instance, not just k8s/flux!


@mcp.tool()
def list_teleport_nodes(cluster: str, filter: Optional[str] = None) -> Dict[str, Any]:
    """
    List available SSH nodes in a Teleport cluster.

    This tool shows which nodes you can SSH to via Teleport.

    ANALOGY: Like running `tsh ls` to see available servers.

    Args:
        cluster: Must be one of ["staging", "production"]
        filter: Optional filter string (e.g., "k8s", "master", "bastion")

    Returns:
        dict: Available nodes information
        {
            "success": bool,
            "cluster": str,
            "nodes": List[Dict],          # List of available nodes
            "message": str,
            "ansible_command": str,
            "ansible_steps": List[str]
        }

    Example Response (Success):
        {
            "success": true,
            "cluster": "staging",
            "nodes": [
                {
                    "hostname": "k8s-master-01",
                    "address": "10.0.1.5:3022",
                    "labels": {"env": "staging", "role": "k8s-master"}
                },
                {
                    "hostname": "k8s-worker-01",
                    "address": "10.0.1.6:3022",
                    "labels": {"env": "staging", "role": "k8s-worker"}
                }
            ],
            "message": "✅ Found 2 node(s) in staging",
            "ansible_command": null,
            "ansible_steps": []
        }

    Example Response (Not Logged In):
        {
            "success": false,
            "cluster": "staging",
            "nodes": [],
            "message": "❌ Not logged into staging cluster",
            "ansible_command": null,
            "ansible_steps": [
                "tsh login --proxy=teleport.tw.ee:443 --auth=okta staging"
            ]
        }

    SECURITY NOTES:
    - Input validation: cluster must be in allow-list
    - Read-only operation
    - Checks authentication first
    """

    # STEP 1: Validate input
    if cluster not in ALLOWED_TELEPORT_CLUSTERS:
        return {
            "success": False,
            "cluster": cluster,
            "nodes": [],
            "message": f"❌ Invalid cluster. Must be one of: {ALLOWED_TELEPORT_CLUSTERS}",
            "ansible_command": None,
            "ansible_steps": [],
        }

    # STEP 2: Verify tsh is installed
    install_check = check_tsh_installed()
    if not install_check["installed"]:
        return {
            "success": False,
            "cluster": cluster,
            "nodes": [],
            "message": "❌ tsh is not installed",
            "ansible_command": install_check["ansible_command"],
            "ansible_steps": install_check["ansible_steps"],
        }

    # STEP 3: List nodes
    command = [TSH_BINARY_PATH, "ls", "--cluster", cluster]

    # Add filter if provided
    if filter:
        # Note: tsh ls doesn't have a built-in filter flag, so we'll filter in post-processing
        pass

    try:
        result = subprocess.run(
            command,
            shell=False,
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode != 0:
            # Check if it's an auth issue
            stderr = result.stderr.lower()
            if "not logged in" in stderr or "login" in stderr:
                return {
                    "success": False,
                    "cluster": cluster,
                    "nodes": [],
                    "message": f"❌ Not logged into {cluster} cluster",
                    "ansible_command": None,
                    "ansible_steps": [
                        f"tsh login --proxy=teleport.tw.ee:443 --auth=okta {cluster}"
                    ],
                }
            else:
                return {
                    "success": False,
                    "cluster": cluster,
                    "nodes": [],
                    "message": f"❌ Error listing nodes: {result.stderr}",
                    "ansible_command": None,
                    "ansible_steps": [
                        f"Run 'tsh ls --cluster {cluster}' manually to debug"
                    ],
                }

        # STEP 4: Parse output
        output = result.stdout.strip()
        nodes = []

        if output:
            lines = output.split("\n")
            # Skip header lines (first 2 lines typically)
            for line in lines[2:] if len(lines) > 2 else []:
                if line.strip() and not line.startswith("-"):
                    # Parse node info (hostname is typically first column)
                    parts = line.split()
                    if parts:
                        hostname = parts[0]
                        # Apply filter if provided
                        if filter and filter.lower() not in hostname.lower():
                            continue

                        nodes.append(
                            {
                                "hostname": hostname,
                                "raw_line": line.strip(),
                            }
                        )

        # STEP 5: Return results
        filter_msg = f" matching '{filter}'" if filter else ""
        if nodes:
            return {
                "success": True,
                "cluster": cluster,
                "filter": filter,
                "nodes": nodes,
                "message": f"✅ Found {len(nodes)} node(s) in {cluster}{filter_msg}",
                "ansible_command": None,
                "ansible_steps": [],
            }
        else:
            return {
                "success": True,
                "cluster": cluster,
                "filter": filter,
                "nodes": [],
                "message": f"⚠️  No nodes found in {cluster}{filter_msg}",
                "ansible_command": None,
                "ansible_steps": [
                    "Verify your Teleport permissions allow SSH access",
                    f"Try: tsh ls --cluster {cluster}",
                ],
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "cluster": cluster,
            "nodes": [],
            "message": f"❌ Command timed out while listing nodes in {cluster}",
            "ansible_command": None,
            "ansible_steps": ["Check network connectivity to Teleport proxy"],
        }
    except Exception as e:
        return {
            "success": False,
            "cluster": cluster,
            "nodes": [],
            "message": f"❌ Unexpected error: {str(e)}",
            "ansible_command": None,
            "ansible_steps": [f"Run 'tsh ls --cluster {cluster}' manually to debug"],
        }


@mcp.tool()
def verify_ssh_access(cluster: str, node: str, user: str = "root") -> Dict[str, Any]:
    """
    Verify you can SSH to a specific node via Teleport.

    This tool tests SSH connectivity by running a simple test command.

    ANALOGY: Like running `tsh ssh user@node "echo test"` to verify access.

    Args:
        cluster: Teleport cluster name ["staging", "production"]
        node: Node hostname (e.g., "k8s-master-01")
        user: SSH user (default: "root")

    Returns:
        dict: Access verification results
        {
            "success": bool,
            "cluster": str,
            "node": str,
            "user": str,
            "accessible": bool,
            "message": str,
            "ansible_command": str,
            "ansible_steps": List[str]
        }

    Example Response (Success):
        {
            "success": true,
            "cluster": "staging",
            "node": "k8s-master-01",
            "user": "root",
            "accessible": true,
            "message": "✅ Successfully connected to root@k8s-master-01 via staging",
            "ansible_command": null,
            "ansible_steps": []
        }

    Example Response (No Access):
        {
            "success": false,
            "cluster": "staging",
            "node": "k8s-master-01",
            "user": "root",
            "accessible": false,
            "message": "❌ Cannot connect to root@k8s-master-01",
            "ansible_command": null,
            "ansible_steps": [
                "Check if node exists: tsh ls --cluster staging",
                "Verify permissions allow SSH access",
                "Try manually: tsh ssh --cluster staging root@k8s-master-01"
            ]
        }

    SECURITY NOTES:
    - Input validation on cluster names
    - Read-only test (just checks access, doesn't modify anything)
    - Uses safe subprocess calls
    - Command is hardcoded (no user input in the test command)
    """

    # STEP 1: Validate inputs
    if cluster not in ALLOWED_TELEPORT_CLUSTERS:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "user": user,
            "accessible": False,
            "message": f"❌ Invalid cluster. Must be one of: {ALLOWED_TELEPORT_CLUSTERS}",
            "ansible_command": None,
            "ansible_steps": [],
        }

    # STEP 2: Verify tsh is installed
    install_check = check_tsh_installed()
    if not install_check["installed"]:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "user": user,
            "accessible": False,
            "message": "❌ tsh is not installed",
            "ansible_command": install_check["ansible_command"],
            "ansible_steps": install_check["ansible_steps"],
        }

    # STEP 3: Test SSH connection with a simple command
    # We run: tsh ssh --cluster=X user@node "echo test"
    target = f"{user}@{node}"
    command = [
        TSH_BINARY_PATH,
        "ssh",
        f"--cluster={cluster}",
        target,
        "echo test",
    ]

    try:
        result = subprocess.run(
            command,
            shell=False,
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode == 0 and "test" in result.stdout:
            return {
                "success": True,
                "cluster": cluster,
                "node": node,
                "user": user,
                "accessible": True,
                "message": f"✅ Successfully connected to {user}@{node} via {cluster}",
                "ansible_command": None,
                "ansible_steps": [],
            }
        else:
            stderr = result.stderr.lower()
            if "not logged in" in stderr or "please login" in stderr:
                return {
                    "success": False,
                    "cluster": cluster,
                    "node": node,
                    "user": user,
                    "accessible": False,
                    "message": f"❌ Not logged into {cluster} Teleport cluster",
                    "ansible_command": None,
                    "ansible_steps": [
                        f"tsh login --proxy=teleport.tw.ee:443 --auth=okta {cluster}",
                        f"tsh ssh --cluster={cluster} {target}",
                    ],
                }
            else:
                return {
                    "success": False,
                    "cluster": cluster,
                    "node": node,
                    "user": user,
                    "accessible": False,
                    "message": f"❌ Cannot connect to {user}@{node}: {result.stderr}",
                    "ansible_command": None,
                    "ansible_steps": [
                        f"Check if node exists: tsh ls --cluster {cluster}",
                        "Verify permissions allow SSH access",
                        f"Try manually: tsh ssh --cluster={cluster} {target}",
                    ],
                }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "user": user,
            "accessible": False,
            "message": "❌ SSH connection timed out",
            "ansible_command": None,
            "ansible_steps": [
                "Check network connectivity",
                f"Verify node is responsive: tsh ssh --cluster={cluster} {target}",
            ],
        }
    except Exception as e:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "user": user,
            "accessible": False,
            "message": f"❌ Unexpected error: {str(e)}",
            "ansible_command": None,
            "ansible_steps": [
                f"Try manually: tsh ssh --cluster={cluster} {target}",
            ],
        }


@mcp.tool()
def run_remote_command(
    cluster: str, node: str, command: str, user: str = "root", timeout: int = 30
) -> Dict[str, Any]:
    """
    Execute a command on a remote node via Teleport SSH.

    THIS IS THE CORE PRIMITIVE - all other high-level tools build on this.

    ANALOGY: Like running `tsh ssh user@node "command"` but with safety checks.

    Args:
        cluster: Teleport cluster name ["staging", "production"]
        node: Node hostname (e.g., "k8s-master-01")
        command: Command to execute (e.g., "kubectl get pods")
        user: SSH user (default: "root")
        timeout: Command timeout in seconds (default: 30)

    Returns:
        dict: Command execution results
        {
            "success": bool,
            "cluster": str,
            "node": str,
            "user": str,
            "command": str,
            "exit_code": int,
            "stdout": str,
            "stderr": str,
            "message": str,
            "ansible_command": str,
            "ansible_steps": List[str]
        }

    Example Response (Success):
        {
            "success": true,
            "cluster": "staging",
            "node": "k8s-master-01",
            "user": "root",
            "command": "kubectl get nodes",
            "exit_code": 0,
            "stdout": "NAME           STATUS   ROLES    AGE   VERSION\\nk8s-master-01   Ready    master   30d   v1.28.0",
            "stderr": "",
            "message": "✅ Command executed successfully",
            "ansible_command": null,
            "ansible_steps": []
        }

    Example Response (Command Failed):
        {
            "success": false,
            "cluster": "staging",
            "node": "k8s-master-01",
            "command": "kubectl get invalid",
            "exit_code": 1,
            "stdout": "",
            "stderr": "Error: resource type invalid not found",
            "message": "❌ Command failed with exit code 1",
            "ansible_command": null,
            "ansible_steps": []
        }

    SECURITY NOTES:
    - Input validation on cluster names
    - Command is passed as a single argument (no shell parsing on remote)
    - Uses shlex.quote() to prevent injection
    - Timeout prevents runaway commands
    - User must be explicitly specified
    """

    # STEP 1: Validate inputs
    if cluster not in ALLOWED_TELEPORT_CLUSTERS:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "user": user,
            "command": command,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "message": f"❌ Invalid cluster. Must be one of: {ALLOWED_TELEPORT_CLUSTERS}",
            "ansible_command": None,
            "ansible_steps": [],
        }

    if not command or not command.strip():
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "user": user,
            "command": command,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "message": "❌ Command cannot be empty",
            "ansible_command": None,
            "ansible_steps": [],
        }

    # STEP 2: Verify tsh is installed
    install_check = check_tsh_installed()
    if not install_check["installed"]:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "user": user,
            "command": command,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "message": "❌ tsh is not installed",
            "ansible_command": install_check["ansible_command"],
            "ansible_steps": install_check["ansible_steps"],
        }

    # STEP 3: Build and execute SSH command
    # Format: tsh ssh --cluster=X user@node "command"
    target = f"{user}@{node}"

    # Build command as list (safe from injection)
    tsh_command = [
        TSH_BINARY_PATH,
        "ssh",
        f"--cluster={cluster}",
        target,
        command,  # Note: this is passed as a single argument to tsh
    ]

    try:
        result = subprocess.run(
            tsh_command,
            shell=False,  # CRITICAL: No shell=True
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        # STEP 4: Build response based on exit code
        if result.returncode == 0:
            return {
                "success": True,
                "cluster": cluster,
                "node": node,
                "user": user,
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "message": "✅ Command executed successfully",
                "ansible_command": None,
                "ansible_steps": [],
            }
        else:
            # Check if it's an SSH/auth issue vs command failure
            stderr = result.stderr.lower()
            if "not logged in" in stderr or "please login" in stderr:
                return {
                    "success": False,
                    "cluster": cluster,
                    "node": node,
                    "user": user,
                    "command": command,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "message": f"❌ Not logged into {cluster} cluster",
                    "ansible_command": None,
                    "ansible_steps": [
                        f"tsh login --proxy=teleport.tw.ee:443 --auth=okta {cluster}"
                    ],
                }
            elif "connection" in stderr or "cannot connect" in stderr:
                return {
                    "success": False,
                    "cluster": cluster,
                    "node": node,
                    "user": user,
                    "command": command,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "message": f"❌ Cannot connect to {user}@{node}",
                    "ansible_command": None,
                    "ansible_steps": [
                        f"Check if node exists: tsh ls --cluster {cluster}",
                        f"Try manually: tsh ssh --cluster={cluster} {target}",
                    ],
                }
            else:
                # Command executed but returned non-zero exit code
                return {
                    "success": False,
                    "cluster": cluster,
                    "node": node,
                    "user": user,
                    "command": command,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "message": f"❌ Command failed with exit code {result.returncode}",
                    "ansible_command": None,
                    "ansible_steps": [
                        "Check stderr output above for error details",
                        f'Try manually: tsh ssh --cluster={cluster} {target} "{command}"',
                    ],
                }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "user": user,
            "command": command,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "message": f"❌ Command timed out after {timeout} seconds",
            "ansible_command": None,
            "ansible_steps": [
                "Command took too long to execute",
                "Consider increasing timeout for long-running commands",
            ],
        }
    except Exception as e:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "user": user,
            "command": command,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "message": f"❌ Unexpected error: {str(e)}",
            "ansible_command": None,
            "ansible_steps": [
                f'Try manually: tsh ssh --cluster={cluster} {target} "{command}"',
            ],
        }


@mcp.tool()
def list_flux_kustomizations(cluster: str, node: str) -> Dict[str, Any]:
    """
    List Flux Kustomizations on a Kubernetes node.

    This is a HIGH-LEVEL tool that uses run_remote_command() internally.

    ANALOGY: Like running `tsh ssh root@node "kubectl get kustomizations -A -o json"`
    but with parsing and error handling.

    Args:
        cluster: Teleport cluster name ["staging", "production"]
        node: K8s node hostname (e.g., "k8s-master-01")

    Returns:
        dict: Flux kustomizations information
        {
            "success": bool,
            "cluster": str,
            "node": str,
            "kustomizations": List[Dict],
            "message": str,
            "ansible_command": str,
            "ansible_steps": List[str]
        }

    Example Response (Success):
        {
            "success": true,
            "cluster": "staging",
            "node": "k8s-master-01",
            "kustomizations": [
                {
                    "name": "flux-system",
                    "namespace": "flux-system",
                    "ready": "True",
                    "message": "Applied revision: main@sha1:abc123",
                    "last_applied_revision": "main@sha1:abc123"
                },
                {
                    "name": "apps",
                    "namespace": "flux-system",
                    "ready": "True",
                    "message": "Applied revision: main@sha1:def456",
                    "last_applied_revision": "main@sha1:def456"
                }
            ],
            "message": "✅ Found 2 Kustomization(s)",
            "ansible_command": null,
            "ansible_steps": []
        }

    SECURITY NOTES:
    - Input validation on cluster names
    - Uses run_remote_command() which has its own security checks
    - Command is hardcoded (no user input in kubectl command)
    """

    # STEP 1: Build kubectl command
    kubectl_command = (
        "sudo kubectl get kustomizations.kustomize.toolkit.fluxcd.io -A -o json"
    )

    # STEP 2: Execute command via SSH
    result = run_remote_command(
        cluster, node, kubectl_command, user="stephen.tan", timeout=30
    )

    if not result["success"]:
        # Command execution failed - return the error
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "kustomizations": [],
            "message": result["message"],
            "ansible_command": result.get("ansible_command"),
            "ansible_steps": result.get("ansible_steps", []),
            "raw_error": result.get("stderr", ""),
        }

    # STEP 3: Parse JSON output
    try:
        data = json.loads(result["stdout"])
        kustomizations = []

        for item in data.get("items", []):
            name = item["metadata"]["name"]
            namespace = item["metadata"]["namespace"]
            status = item.get("status", {})

            # Get ready condition
            ready = "Unknown"
            message = ""
            for condition in status.get("conditions", []):
                if condition.get("type") == "Ready":
                    ready = condition.get("status", "Unknown")
                    message = condition.get("message", "")
                    break

            kustomizations.append(
                {
                    "name": name,
                    "namespace": namespace,
                    "ready": ready,
                    "message": message,
                    "last_applied_revision": status.get("lastAppliedRevision", "N/A"),
                }
            )

        # STEP 4: Return results
        return {
            "success": True,
            "cluster": cluster,
            "node": node,
            "kustomizations": kustomizations,
            "message": f"✅ Found {len(kustomizations)} Kustomization(s)",
            "ansible_command": None,
            "ansible_steps": [],
        }

    except json.JSONDecodeError as e:
        # Check if Flux might not be installed
        if (
            "error" in result["stderr"].lower()
            or "not found" in result["stderr"].lower()
        ):
            return {
                "success": False,
                "cluster": cluster,
                "node": node,
                "kustomizations": [],
                "message": "❌ Flux may not be installed on this cluster",
                "ansible_command": None,
                "ansible_steps": [
                    f"Verify Flux is installed: tsh ssh --cluster={cluster} root@{node} 'flux check'",
                    "Check kubectl access works: kubectl get ns flux-system",
                ],
                "raw_error": result.get("stderr", ""),
            }
        else:
            return {
                "success": False,
                "cluster": cluster,
                "node": node,
                "kustomizations": [],
                "message": f"❌ Error parsing kubectl output: {str(e)}",
                "ansible_command": None,
                "ansible_steps": [
                    "Command executed but output was not valid JSON",
                    f"Try manually: tsh ssh --cluster={cluster} root@{node} 'flux get kustomizations'",
                ],
                "raw_output": result.get("stdout", "")[:500],  # First 500 chars
            }
    except Exception as e:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "kustomizations": [],
            "message": f"❌ Unexpected error: {str(e)}",
            "ansible_command": None,
            "ansible_steps": [
                f"Try manually: tsh ssh --cluster={cluster} root@{node} 'flux get kustomizations'"
            ],
        }


@mcp.tool()
def get_kustomization_details(
    cluster: str, node: str, name: str, namespace: str = "flux-system"
) -> Dict[str, Any]:
    """
    Get detailed information about a specific Flux Kustomization.

    This tool retrieves comprehensive details about a Kustomization that
    list_flux_kustomizations() doesn't show, including suspend status,
    source reference, path, interval, and reconciliation status.

    ANALOGY: Like running `kubectl get kustomization X -n Y -o json` but
    with parsed, human-readable output.

    Args:
        cluster: Teleport cluster name ["staging", "production"]
        node: K8s node hostname (e.g., "k8s-master-01")
        name: Kustomization name (e.g., "flux-system", "apps")
        namespace: Kustomization namespace (default: "flux-system")

    Returns:
        dict: Detailed kustomization information
        {
            "success": bool,
            "cluster": str,
            "node": str,
            "name": str,
            "namespace": str,
            "details": {
                "suspended": bool,
                "source_ref": {"kind": str, "name": str, "namespace": str},
                "path": str,
                "interval": str,
                "last_applied_revision": str,
                "conditions": List[dict]
            },
            "message": str,
            "ansible_command": str,
            "ansible_steps": List[str]
        }

    Example Response:
        {
            "success": true,
            "cluster": "staging",
            "node": "k8s-master-01",
            "name": "apps",
            "namespace": "flux-system",
            "details": {
                "suspended": false,
                "source_ref": {
                    "kind": "GitRepository",
                    "name": "flux-system",
                    "namespace": "flux-system"
                },
                "path": "./clusters/staging/apps",
                "interval": "10m",
                "last_applied_revision": "main@sha1:abc123",
                "conditions": [
                    {"type": "Ready", "status": "True", "reason": "ReconciliationSucceeded"}
                ]
            },
            "message": "✅ Retrieved details for kustomization 'apps'",
            "ansible_command": null,
            "ansible_steps": []
        }

    SECURITY NOTES:
    - Input validation on cluster names
    - Uses shlex.quote() for name/namespace to prevent injection
    - Read-only operation (just queries state)

    DESIGN VALIDATION (MW-002 Step 2):
    - Layer: TEAM (Flux-specific)
    - Dependencies: run_remote_command() (Platform primitive)
    - Configuration: Cluster/node/name as parameters (not hardcoded)
    - Testing: Can mock run_remote_command()
    - Red flags: None detected
    """

    # Safely quote user inputs to prevent injection
    safe_name = shlex.quote(name)
    safe_namespace = shlex.quote(namespace)

    # Build kubectl command to get kustomization details as JSON
    kubectl_command = (
        f"sudo kubectl get kustomization {safe_name} -n {safe_namespace} -o json"
    )

    # Execute command via Platform primitive
    result = run_remote_command(
        cluster=cluster, node=node, command=kubectl_command, user="root", timeout=30
    )

    # Check if command failed
    if not result["success"]:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "name": name,
            "namespace": namespace,
            "details": {},
            "message": f"❌ Failed to get kustomization details: {result['message']}",
            "ansible_command": result.get("ansible_command"),
            "ansible_steps": result.get("ansible_steps", []),
        }

    # Parse JSON output
    try:
        kustomization = json.loads(result["stdout"])

        # Extract key details
        spec = kustomization.get("spec", {})
        status = kustomization.get("status", {})

        details = {
            "suspended": spec.get("suspend", False),
            "source_ref": spec.get("sourceRef", {}),
            "path": spec.get("path", ""),
            "interval": spec.get("interval", ""),
            "prune": spec.get("prune", False),
            "last_applied_revision": status.get("lastAppliedRevision", ""),
            "last_attempted_revision": status.get("lastAttemptedRevision", ""),
            "conditions": status.get("conditions", []),
        }

        # Determine overall status
        ready = False
        for condition in details["conditions"]:
            if condition.get("type") == "Ready" and condition.get("status") == "True":
                ready = True
                break

        status_emoji = "✅" if ready else "⚠️"
        suspend_status = " (SUSPENDED)" if details["suspended"] else ""

        return {
            "success": True,
            "cluster": cluster,
            "node": node,
            "name": name,
            "namespace": namespace,
            "details": details,
            "message": f"{status_emoji} Retrieved details for kustomization '{name}'{suspend_status}",
            "ansible_command": None,
            "ansible_steps": [],
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "name": name,
            "namespace": namespace,
            "details": {},
            "message": f"❌ Error parsing kubectl output: {str(e)}",
            "ansible_command": None,
            "ansible_steps": [
                f"Try manually: tsh ssh --cluster={cluster} root@{node} 'kubectl get kustomization {name} -n {namespace}'",
                "Check if Flux is installed: flux check",
            ],
            "raw_output": result.get("stdout", "")[:500],
        }
    except Exception as e:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "name": name,
            "namespace": namespace,
            "details": {},
            "message": f"❌ Unexpected error: {str(e)}",
            "ansible_command": None,
            "ansible_steps": [
                f"Try manually: tsh ssh --cluster={cluster} root@{node} 'kubectl get kustomization {name} -n {namespace} -o json'"
            ],
        }


@mcp.tool()
def reconcile_flux_kustomization(
    cluster: str, node: str, name: str, namespace: str = "flux-system"
) -> Dict[str, Any]:
    """
    Trigger a Flux reconciliation for a specific Kustomization.

    This is a HIGH-LEVEL tool that uses run_remote_command() internally.

    ANALOGY: Like running `tsh ssh root@node "flux reconcile kustomization X -n Y"`

    Args:
        cluster: Teleport cluster name ["staging", "production"]
        node: K8s node hostname (e.g., "k8s-master-01")
        name: Kustomization name (e.g., "flux-system", "apps")
        namespace: Kustomization namespace (default: "flux-system")

    Returns:
        dict: Reconciliation results
        {
            "success": bool,
            "cluster": str,
            "node": str,
            "name": str,
            "namespace": str,
            "message": str,
            "output": str,
            "ansible_command": str,
            "ansible_steps": List[str]
        }

    Example Response (Success):
        {
            "success": true,
            "cluster": "staging",
            "node": "k8s-master-01",
            "name": "flux-system",
            "namespace": "flux-system",
            "message": "✅ Reconciliation triggered successfully",
            "output": "► annotating Kustomization flux-system in flux-system namespace\\n◎ waiting for Kustomization reconciliation\\n✔ Kustomization reconciliation completed",
            "ansible_command": null,
            "ansible_steps": []
        }

    SECURITY NOTES:
    - Input validation on cluster names
    - Uses run_remote_command() which has its own security checks
    - Uses shlex.quote() for user-provided name/namespace to prevent injection
    """

    # STEP 1: Build flux reconcile command (with injection protection)
    # Use shlex.quote() to safely include user-provided strings
    safe_name = shlex.quote(name)
    safe_namespace = shlex.quote(namespace)
    flux_command = f"sudo flux reconcile kustomization {safe_name} -n {safe_namespace}"

    # STEP 2: Execute command via SSH
    result = run_remote_command(
        cluster, node, flux_command, user="stephen.tan", timeout=60
    )

    if result["success"]:
        return {
            "success": True,
            "cluster": cluster,
            "node": node,
            "name": name,
            "namespace": namespace,
            "message": "✅ Reconciliation triggered successfully",
            "output": result["stdout"],
            "ansible_command": None,
            "ansible_steps": [],
        }
    else:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "name": name,
            "namespace": namespace,
            "message": f"❌ Reconciliation failed: {result['message']}",
            "output": result.get("stderr", ""),
            "ansible_command": result.get("ansible_command"),
            "ansible_steps": result.get("ansible_steps", []),
        }


# =============================================================================
# V1c TOOLS: Complete Flux Management Suite
# =============================================================================
# These tools extend Flux capabilities beyond basic list/reconcile operations.
# They enable full GitOps workflow management: suspend, resume, view sources, logs.
#
# Philosophy: "Complete operational control" - everything you need to manage Flux


@mcp.tool()
def list_flux_sources(cluster: str, node: str) -> Dict[str, Any]:
    """
    List all Flux GitRepository sources.

    This shows what Git repositories Flux is watching for changes.

    ANALOGY: Like running `flux get sources git` to see your GitOps sources.

    Args:
        cluster: Teleport cluster name ["staging", "production"]
        node: K8s node hostname (e.g., "k8s-master-01")

    Returns:
        dict: Flux GitRepository sources
        {
            "success": bool,
            "cluster": str,
            "node": str,
            "sources": List[Dict],
            "message": str,
            "ansible_command": str,
            "ansible_steps": List[str]
        }

    SECURITY NOTES:
    - Input validation on cluster names
    - Uses run_remote_command() internally
    - Read-only operation
    """

    # Build kubectl command to get GitRepository sources
    kubectl_command = (
        "sudo kubectl get gitrepositories.source.toolkit.fluxcd.io -A -o json"
    )

    # Execute command via SSH
    result = run_remote_command(
        cluster, node, kubectl_command, user="stephen.tan", timeout=30
    )

    if not result["success"]:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "sources": [],
            "message": result["message"],
            "ansible_command": result.get("ansible_command"),
            "ansible_steps": result.get("ansible_steps", []),
        }

    # Parse JSON output
    try:
        data = json.loads(result["stdout"])
        sources = []

        for item in data.get("items", []):
            name = item["metadata"]["name"]
            namespace = item["metadata"]["namespace"]
            spec = item.get("spec", {})
            status = item.get("status", {})

            # Get ready condition
            ready = "Unknown"
            message = ""
            for condition in status.get("conditions", []):
                if condition.get("type") == "Ready":
                    ready = condition.get("status", "Unknown")
                    message = condition.get("message", "")
                    break

            sources.append(
                {
                    "name": name,
                    "namespace": namespace,
                    "url": spec.get("url", "N/A"),
                    "ref": spec.get("ref", {}),
                    "ready": ready,
                    "message": message,
                    "artifact": status.get("artifact", {}).get("revision", "N/A"),
                }
            )

        return {
            "success": True,
            "cluster": cluster,
            "node": node,
            "sources": sources,
            "message": f"✅ Found {len(sources)} GitRepository source(s)",
            "ansible_command": None,
            "ansible_steps": [],
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "sources": [],
            "message": f"❌ Error parsing kubectl output: {str(e)}",
            "ansible_command": None,
            "ansible_steps": [
                f"Try manually: tsh ssh --cluster={cluster} root@{node} 'flux get sources git'"
            ],
        }


@mcp.tool()
def suspend_flux_kustomization(
    cluster: str, node: str, name: str, namespace: str = "flux-system"
) -> Dict[str, Any]:
    """
    Suspend a Flux Kustomization (pause reconciliation).

    This stops Flux from reconciling the kustomization until resumed.

    ANALOGY: Like running `flux suspend kustomization X` to pause deployments.

    Args:
        cluster: Teleport cluster name ["staging", "production"]
        node: K8s node hostname (e.g., "k8s-master-01")
        name: Kustomization name (e.g., "apps", "infrastructure")
        namespace: Kustomization namespace (default: "flux-system")

    Returns:
        dict: Suspension results
        {
            "success": bool,
            "cluster": str,
            "node": str,
            "name": str,
            "namespace": str,
            "message": str,
            "output": str,
            "ansible_command": str,
            "ansible_steps": List[str]
        }

    SECURITY NOTES:
    - Input validation on cluster names
    - Uses shlex.quote() for user input
    - Modifies cluster state (use with caution)
    """

    # Build flux suspend command (with injection protection)
    safe_name = shlex.quote(name)
    safe_namespace = shlex.quote(namespace)
    flux_command = f"sudo flux suspend kustomization {safe_name} -n {safe_namespace}"

    # Execute command via SSH
    result = run_remote_command(
        cluster, node, flux_command, user="stephen.tan", timeout=30
    )

    if result["success"]:
        return {
            "success": True,
            "cluster": cluster,
            "node": node,
            "name": name,
            "namespace": namespace,
            "message": f"✅ Suspended {name} in {namespace}",
            "output": result["stdout"],
            "ansible_command": None,
            "ansible_steps": [],
        }
    else:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "name": name,
            "namespace": namespace,
            "message": f"❌ Failed to suspend: {result['message']}",
            "output": result.get("stderr", ""),
            "ansible_command": result.get("ansible_command"),
            "ansible_steps": result.get("ansible_steps", []),
        }


@mcp.tool()
def resume_flux_kustomization(
    cluster: str, node: str, name: str, namespace: str = "flux-system"
) -> Dict[str, Any]:
    """
    Resume a suspended Flux Kustomization.

    This resumes reconciliation for a previously suspended kustomization.

    ANALOGY: Like running `flux resume kustomization X` to restart deployments.

    Args:
        cluster: Teleport cluster name ["staging", "production"]
        node: K8s node hostname (e.g., "k8s-master-01")
        name: Kustomization name (e.g., "apps", "infrastructure")
        namespace: Kustomization namespace (default: "flux-system")

    Returns:
        dict: Resume results
        {
            "success": bool,
            "cluster": str,
            "node": str,
            "name": str,
            "namespace": str,
            "message": str,
            "output": str,
            "ansible_command": str,
            "ansible_steps": List[str]
        }

    SECURITY NOTES:
    - Input validation on cluster names
    - Uses shlex.quote() for user input
    - Modifies cluster state (use with caution)
    """

    # Build flux resume command (with injection protection)
    safe_name = shlex.quote(name)
    safe_namespace = shlex.quote(namespace)
    flux_command = f"sudo flux resume kustomization {safe_name} -n {safe_namespace}"

    # Execute command via SSH
    result = run_remote_command(
        cluster, node, flux_command, user="stephen.tan", timeout=30
    )

    if result["success"]:
        return {
            "success": True,
            "cluster": cluster,
            "node": node,
            "name": name,
            "namespace": namespace,
            "message": f"✅ Resumed {name} in {namespace}",
            "output": result["stdout"],
            "ansible_command": None,
            "ansible_steps": [],
        }
    else:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "name": name,
            "namespace": namespace,
            "message": f"❌ Failed to resume: {result['message']}",
            "output": result.get("stderr", ""),
            "ansible_command": result.get("ansible_command"),
            "ansible_steps": result.get("ansible_steps", []),
        }


@mcp.tool()
def get_flux_logs(
    cluster: str, node: str, component: str = "kustomize-controller", tail: int = 50
) -> Dict[str, Any]:
    """
    Get logs from a Flux component.

    This shows recent logs from Flux controllers for debugging.

    ANALOGY: Like running `flux logs` to see what Flux is doing.

    Args:
        cluster: Teleport cluster name ["staging", "production"]
        node: K8s node hostname (e.g., "k8s-master-01")
        component: Flux component ["kustomize-controller", "source-controller",
                   "helm-controller", "notification-controller"]
        tail: Number of lines to show (default: 50)

    Returns:
        dict: Log output
        {
            "success": bool,
            "cluster": str,
            "node": str,
            "component": str,
            "logs": str,
            "message": str,
            "ansible_command": str,
            "ansible_steps": List[str]
        }

    SECURITY NOTES:
    - Input validation on cluster names
    - Component name is validated against allow-list
    - Read-only operation
    """

    # Validate component name
    allowed_components = [
        "kustomize-controller",
        "source-controller",
        "helm-controller",
        "notification-controller",
    ]
    if component not in allowed_components:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "component": component,
            "logs": "",
            "message": f"❌ Invalid component. Must be one of: {allowed_components}",
            "ansible_command": None,
            "ansible_steps": [],
        }

    # Build kubectl logs command
    kubectl_command = (
        f"sudo kubectl logs -n flux-system deploy/{component} --tail={tail}"
    )

    # Execute command via SSH
    result = run_remote_command(
        cluster, node, kubectl_command, user="stephen.tan", timeout=30
    )

    if result["success"]:
        return {
            "success": True,
            "cluster": cluster,
            "node": node,
            "component": component,
            "logs": result["stdout"],
            "message": f"✅ Retrieved {tail} lines from {component}",
            "ansible_command": None,
            "ansible_steps": [],
        }
    else:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "component": component,
            "logs": result.get("stderr", ""),
            "message": f"❌ Failed to get logs: {result['message']}",
            "ansible_command": result.get("ansible_command"),
            "ansible_steps": result.get("ansible_steps", []),
        }


@mcp.tool()
def get_kustomization_events(
    cluster: str, node: str, name: str, namespace: str = "flux-system"
) -> Dict[str, Any]:
    """
    Get Kubernetes events for a specific Kustomization.

    This shows recent events related to a kustomization for debugging.

    ANALOGY: Like running `kubectl describe kustomization X` to see events.

    Args:
        cluster: Teleport cluster name ["staging", "production"]
        node: K8s node hostname (e.g., "k8s-master-01")
        name: Kustomization name (e.g., "apps", "infrastructure")
        namespace: Kustomization namespace (default: "flux-system")

    Returns:
        dict: Events information
        {
            "success": bool,
            "cluster": str,
            "node": str,
            "name": str,
            "namespace": str,
            "events": str,
            "message": str,
            "ansible_command": str,
            "ansible_steps": List[str]
        }

    SECURITY NOTES:
    - Input validation on cluster names
    - Uses shlex.quote() for user input
    - Read-only operation
    """

    # Build kubectl get events command (with injection protection)
    safe_name = shlex.quote(name)
    safe_namespace = shlex.quote(namespace)
    kubectl_command = f"sudo kubectl get events -n {safe_namespace} --field-selector involvedObject.name={safe_name} --sort-by='.lastTimestamp'"

    # Execute command via SSH
    result = run_remote_command(
        cluster, node, kubectl_command, user="stephen.tan", timeout=30
    )

    if result["success"]:
        return {
            "success": True,
            "cluster": cluster,
            "node": node,
            "name": name,
            "namespace": namespace,
            "events": result["stdout"],
            "message": f"✅ Retrieved events for {name}",
            "ansible_command": None,
            "ansible_steps": [],
        }
    else:
        return {
            "success": False,
            "cluster": cluster,
            "node": node,
            "name": name,
            "namespace": namespace,
            "events": result.get("stderr", ""),
            "message": f"❌ Failed to get events: {result['message']}",
            "ansible_command": result.get("ansible_command"),
            "ansible_steps": result.get("ansible_steps", []),
        }


# =============================================================================
# DECORATOR EXPLANATION (for the Python newbie)
# =============================================================================
"""
What is @mcp.tool() doing?

ANALOGY: Think of it as a "registration wrapper script"

In Bash, you might have a directory of scripts:
    /usr/local/bin/
        - my-command-1
        - my-command-2

The @mcp.tool() decorator is like a script that:
1. Takes your function (list_kube_contexts)
2. "Registers" it with the MCP server
3. Makes it available to the AI as a "tool"

Without the decorator: Just a regular Python function
With the decorator:    A tool the AI can discover and call

The decorator also reads your docstring (the triple-quoted text) and type hints
to tell the AI:
- What the tool does
- What inputs it needs (none in this case)
- What output it returns (a string)
"""


# =============================================================================
# TYPE HINTS EXPLANATION
# =============================================================================
"""
What is `-> str` doing after the function name?

ANALOGY: It's like declaring variable types in strongly-typed languages

In Ansible, you might document a variable:
    # @var string package_name - The name of the package to install

In Python type hints:
    def install_package(package_name: str) -> bool:
        #                 ^^^^ input type   ^^^^ return type

This tells:
1. The AI: "This function returns a string"
2. Your IDE: "Auto-complete and warn me if I use it wrong"
3. Other developers: "Here's the contract/API"

Type hints DON'T enforce anything at runtime - they're just documentation
that tools (like the MCP server) can read programmatically.
"""


# =============================================================================
# DOCSTRING EXPLANATION
# =============================================================================
"""
What is the triple-quoted string (docstring) doing?

ANALOGY: It's the README.md for your function

When you write an Ansible role, you create:
    roles/my-role/
        README.md        <- Explains what the role does
        tasks/main.yml   <- The actual implementation

In Python:
    def my_tool():
        \"\"\"This is the README\"\"\"  <- Docstring (the documentation)
        return "result"               <- The implementation

The MCP server reads this docstring and sends it to the AI, so the AI knows:
- What the tool does
- What parameters it needs
- What it returns
- Any security notes or examples

This is your "API contract" with the AI. If the docstring is unclear,
the AI will use the tool wrong!
"""


# =============================================================================
# SERVER STARTUP
# =============================================================================

if __name__ == "__main__":
    # This block runs when you execute: python platform_mcp.py
    # ANALOGY: Like the "main:" section in an Ansible playbook

    # Start the MCP server
    # This will listen for requests from your AI agent (Claude Desktop, Zed, etc.)
    mcp.run()
