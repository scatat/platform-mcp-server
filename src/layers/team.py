"""
MCP Server - Team Layer

This module contains team-layer tools as defined in the 3-layer architecture.

Layer: team
"""

import json
import os
import re
import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def list_flux_kustomizations(
    cluster: str, node: str, show_suspend: bool = False
) -> Dict[str, Any]:
    """
    List Flux Kustomizations on a Kubernetes node.

    This is a HIGH-LEVEL tool that uses run_remote_command() internally.

    ANALOGY: Like running `tsh ssh root@node "kubectl get kustomizations -A -o json"`
    but with parsing and error handling.

    Args:
        cluster: Teleport cluster name ["staging", "production"]
        node: K8s node hostname (e.g., "k8s-master-01")
        show_suspend: Include suspend status in output (default: False)

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
                    "last_applied_revision": "main@sha1:abc123",
                    "suspended": false  # Only if show_suspend=True
                },
                {
                    "name": "apps",
                    "namespace": "flux-system",
                    "ready": "True",
                    "message": "Applied revision: main@sha1:def456",
                    "last_applied_revision": "main@sha1:def456",
                    "suspended": false  # Only if show_suspend=True
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

            kustomization_info = {
                "name": name,
                "namespace": namespace,
                "ready": ready,
                "message": message,
                "last_applied_revision": status.get("lastAppliedRevision", "N/A"),
            }

            # Optionally include suspend status
            if show_suspend:
                kustomization_info["suspended"] = spec.get("suspend", False)

            kustomizations.append(kustomization_info)

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
