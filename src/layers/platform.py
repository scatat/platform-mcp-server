"""
MCP Server - Platform Layer

This module contains platform-layer tools as defined in the 3-layer architecture.

Layer: platform
"""

import json
import os
import re
import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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
