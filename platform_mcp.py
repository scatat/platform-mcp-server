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
ALLOWED_TELEPORT_CLUSTERS = ["staging", "production"]

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

    # STEP 1: Check if tsh binary exists at expected path
    # ANALOGY: Like running `which tsh` or `test -f /usr/local/bin/tsh`
    tsh_exists = os.path.isfile(TSH_BINARY_PATH) and os.access(TSH_BINARY_PATH, os.X_OK)

    if tsh_exists:
        # STEP 2a: tsh is installed - return success
        return {
            "installed": True,
            "path": TSH_BINARY_PATH,
            "message": f"✅ tsh is installed at {TSH_BINARY_PATH}",
            "ansible_command": None,
            "ansible_steps": [],
        }
    else:
        # STEP 2b: tsh is NOT installed - provide Ansible guidance
        # ANALOGY: Like a pre-flight check failing and telling you how to fix it
        return {
            "installed": False,
            "path": None,
            "message": "❌ tsh (Teleport CLI) is not installed",
            "ansible_command": f"ansible-playbook {ANSIBLE_MAC_PATH}/playbooks/teleport.yml",
            "ansible_steps": [
                f"cd {ANSIBLE_MAC_PATH}",
                "ansible-playbook playbooks/teleport.yml",
                "This will install tsh v17.7.1 (compatible with all clusters)",
                "Verify installation: tsh version",
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

    # STEP 1: Check if tsh is installed first
    # ANALOGY: Like checking if a tool exists before trying to run it
    install_check = check_tsh_installed()

    if not install_check["installed"]:
        # STEP 2a: tsh not installed - return guidance from check_tsh_installed()
        return {
            "success": False,
            "version": None,
            "full_version": None,
            "message": install_check["message"],
            "ansible_command": install_check["ansible_command"],
            "ansible_steps": install_check["ansible_steps"],
        }

    # STEP 2b: tsh is installed - get version
    try:
        # Run: tsh version
        # SECURITY: No user input, shell=False, safe command
        result = subprocess.run(
            [TSH_BINARY_PATH, "version"],
            shell=False,
            capture_output=True,
            text=True,
            check=True,
        )

        # STEP 3: Parse version from output
        # Expected format: "Teleport v17.7.1 git:v17.7.1-0-g54d391f go1.22.9"
        # ANALOGY: Like using grep/sed to extract version from command output
        version_line = result.stdout.strip().split("\n")[0]

        # Extract version number using regex
        # Pattern: "Teleport v" followed by version number (e.g., "17.7.1")
        version_match = re.search(r"Teleport v([\d.]+)", version_line)
        version = version_match.group(1) if version_match else "unknown"

        return {
            "success": True,
            "version": version,
            "full_version": version_line,
            "message": f"✅ tsh client version: {version}",
            "ansible_command": None,
            "ansible_steps": [],
        }

    except subprocess.CalledProcessError as e:
        # STEP 4: Handle command execution errors
        return {
            "success": False,
            "version": None,
            "full_version": None,
            "message": f"❌ Error running tsh version: {e.stderr}",
            "ansible_command": None,
            "ansible_steps": [],
        }
    except Exception as e:
        # STEP 5: Handle unexpected errors
        return {
            "success": False,
            "version": None,
            "full_version": None,
            "message": f"❌ Unexpected error getting tsh version: {str(e)}",
            "ansible_command": None,
            "ansible_steps": [],
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

    # STEP 1: Validate cluster input
    # SECURITY: Only allow staging or production (prevent injection)
    # ANALOGY: Like checking a parameter against an allow-list in a firewall
    if cluster not in ALLOWED_TELEPORT_CLUSTERS:
        return {
            "success": False,
            "cluster": cluster,
            "proxy_version": None,
            "proxy_url": None,
            "client_version": None,
            "compatible": False,
            "message": f"❌ Invalid cluster: '{cluster}'. Must be one of {ALLOWED_TELEPORT_CLUSTERS}",
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
            "message": install_check["message"],
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
            "message": client_info["message"],
            "ansible_command": client_info.get("ansible_command"),
            "ansible_steps": client_info.get("ansible_steps", []),
        }

    client_version = client_info["version"]

    # STEP 4: Get proxy version
    # Run: tsh version (shows proxy info when logged in)
    try:
        result = subprocess.run(
            [TSH_BINARY_PATH, "version"],
            shell=False,
            capture_output=True,
            text=True,
            check=True,
        )

        # STEP 5: Parse proxy version from output
        # Expected format includes line: "Proxy version: 17.7.1"
        proxy_version = None
        proxy_url = None

        for line in result.stdout.split("\n"):
            if "Proxy version:" in line:
                # Extract version number
                match = re.search(r"Proxy version:\s*([\d.]+)", line)
                if match:
                    proxy_version = match.group(1)
            elif "Proxy:" in line:
                # Extract proxy URL
                match = re.search(r"Proxy:\s*(.+)", line)
                if match:
                    proxy_url = match.group(1).strip()

        if not proxy_version:
            return {
                "success": False,
                "cluster": cluster,
                "proxy_version": None,
                "proxy_url": proxy_url,
                "client_version": client_version,
                "compatible": False,
                "message": f"❌ Could not determine proxy version for {cluster}. Are you logged in?",
                "ansible_command": None,
                "ansible_steps": [
                    f"Login to {cluster}: tsh login --proxy=teleport.tw.ee:443",
                    f"Then try again",
                ],
            }

        # STEP 6: Check compatibility
        # RULE: client_version <= proxy_version is safe (backwards compatible)
        #       client_version > proxy_version may fail (no forward compatibility)
        def version_tuple(v):
            """Convert version string to tuple for comparison"""
            return tuple(map(int, v.split(".")))

        client_tuple = version_tuple(client_version)
        proxy_tuple = version_tuple(proxy_version)
        compatible = client_tuple <= proxy_tuple

        # STEP 7: Build response with guidance
        if client_tuple == proxy_tuple:
            # Perfect match
            message = f"✅ Client ({client_version}) matches {cluster} proxy ({proxy_version})"
            ansible_command = None
            ansible_steps = []
        elif client_tuple < proxy_tuple:
            # Client older - backwards compatible but suggest upgrade
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
            # Client newer - may not work!
            message = f"❌ Client ({client_version}) is NEWER than {cluster} proxy ({proxy_version}). This may cause compatibility issues!"
            ansible_command = f"ansible-playbook {ANSIBLE_MAC_PATH}/playbooks/teleport.yml -e 'teleport_version={proxy_version}'"
            ansible_steps = [
                f"⚠️  DOWNGRADE REQUIRED",
                f"cd {ANSIBLE_MAC_PATH}",
                f"Edit roles/teleport/defaults/main.yml",
                f"Update: teleport_version: '{proxy_version}'",
                "ansible-playbook playbooks/teleport.yml",
                "Verify: tsh version",
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

    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "cluster": cluster,
            "proxy_version": None,
            "proxy_url": None,
            "client_version": client_version,
            "compatible": False,
            "message": f"❌ Error checking {cluster} proxy: {e.stderr}",
            "ansible_command": None,
            "ansible_steps": [],
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
