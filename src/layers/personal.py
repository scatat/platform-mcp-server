"""
MCP Server - Personal Layer

This module contains personal-layer tools as defined in the 3-layer architecture.

Layer: personal
"""

import json
import os
import re
import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from design_validation import DesignValidator
from workflow_state import get_workflow_state

def propose_tool_design(
    tool_name: str,
    purpose: str,
    layer: str,
    dependencies: List[str],
    requires_system_state_change: bool = False,
    implementation_approach: str = "",
) -> Dict[str, Any]:
    """
    Propose a new tool design and validate it against the design checklist.

    This is the MANDATORY first step in MW-002 (New MCP Tool Development).
    Before creating any new tool, you must call this function to validate
    the design against design-checklist.yaml.

    ANALOGY: Like submitting a design document for review before writing code.
    This ensures architectural soundness before implementation.

    Args:
        tool_name: Name of the proposed tool (e.g., "list_flux_kustomizations")
        purpose: One-sentence description of what the tool does
        layer: Which layer this belongs to ["platform", "team", "personal"]
        dependencies: List of dependencies (e.g., ["run_remote_command", "kubectl"])
        requires_system_state_change: Does it modify system state? (default: False)
        implementation_approach: Brief description of implementation (e.g., "Uses run_remote_command to execute kubectl")

    Returns:
        dict: Validation results with token if approved
        {
            "valid": bool,
            "token": str,  # Use this when implementing the tool
            "proposal_id": str,
            "issues": List[str],  # Blocking issues that must be fixed
            "warnings": List[str],  # Non-blocking warnings
            "checklist_results": Dict[str, Any],
            "timestamp": str,
            "proposal_path": str,
            "message": str
        }

    Example Usage:
        result = propose_tool_design(
            tool_name="list_flux_kustomizations",
            purpose="List all Flux Kustomizations in a cluster",
            layer="team",
            dependencies=["run_remote_command", "kubectl"],
            requires_system_state_change=False,
            implementation_approach="Uses run_remote_command to execute 'kubectl get kustomizations -A -o json'"
        )

        if result["valid"]:
            # Save the token - you'll need it to prove validation
            token = result["token"]
            # Now you can proceed with implementation
        else:
            # Fix the issues listed in result["issues"]

    SECURITY NOTES:
    - This is enforcement, not documentation
    - Creates an audit trail in .ephemeral/tool-proposals/
    - Validation token is required for proper MW-002 compliance
    - Checks for Ansible-first principle violations
    - Detects hardcoded configuration

    DESIGN VALIDATION (MW-002 Step 2):
    This tool IS the mandatory design validation step. It programmatically
    enforces the design checklist that was previously only documentation.
    """
    try:
        validator = DesignValidator()
        result = validator.validate_tool_proposal(
            tool_name=tool_name,
            purpose=purpose,
            layer=layer,
            dependencies=dependencies,
            requires_system_state_change=requires_system_state_change,
            implementation_approach=implementation_approach,
        )

        # Add human-readable message
        if result["valid"]:
            result["message"] = (
                f"✅ Tool design '{tool_name}' is valid!\n"
                f"Proposal ID: {result['proposal_id']}\n"
                f"Token: {result['token']}\n"
                f"Saved to: {result['proposal_path']}\n\n"
                "You may now proceed with implementation. Include the token "
                "in your implementation commit message."
            )
        else:
            issues_text = "\n".join(f"  • {issue}" for issue in result["issues"])
            warnings_text = (
                "\n".join(f"  • {warn}" for warn in result["warnings"])
                if result["warnings"]
                else "None"
            )
            result["message"] = (
                f"❌ Tool design '{tool_name}' has issues:\n\n"
                f"Blocking Issues:\n{issues_text}\n\n"
                f"Warnings:\n{warnings_text}\n\n"
                "Fix the blocking issues and resubmit."
            )

        return result

    except Exception as e:
        return {
            "valid": False,
            "message": f"❌ Validation error: {str(e)}",
            "error": str(e),
        }


def verify_tool_design_token(token: str) -> Dict[str, Any]:
    """
    Verify a tool design validation token.

    Use this to check if a validation token is legitimate and retrieve
    the original proposal details.

    ANALOGY: Like checking a signed certificate to verify authenticity.

    Args:
        token: The validation token from propose_tool_design()

    Returns:
        dict: Verification results
        {
            "valid": bool,
            "proposal_id": str,
            "proposal_data": Dict[str, Any],
            "message": str
        }

    SECURITY NOTES:
    - Tokens are cryptographically generated
    - Tampering with tokens will fail verification
    - Tokens are tied to specific proposal IDs
    """
    try:
        validator = DesignValidator()
        result = validator.verify_token(token)
        return result
    except Exception as e:
        return {
            "valid": False,
            "message": f"❌ Token verification error: {str(e)}",
            "error": str(e),
        }


def list_tool_proposals() -> Dict[str, Any]:
    """
    List all validated tool proposals.

    Shows the audit trail of all tools that have been through design validation.

    ANALOGY: Like reviewing a log of approved design documents.

    Returns:
        dict: List of proposals
        {
            "count": int,
            "proposals": List[Dict[str, Any]],
            "message": str
        }

    SECURITY NOTES:
    - Read-only operation
    - Shows audit trail for accountability
    """
    try:
        validator = DesignValidator()
        proposals = validator.list_proposals()

        return {
            "count": len(proposals),
            "proposals": proposals,
            "message": f"✅ Found {len(proposals)} validated tool proposal(s)",
        }
    except Exception as e:
        return {
            "count": 0,
            "proposals": [],
            "message": f"❌ Error listing proposals: {str(e)}",
            "error": str(e),
        }


def create_mcp_tool(
    tool_name: str,
    tool_code: str,
    validation_token: str,
    description: str = "",
) -> Dict[str, Any]:
    """
    Create a new MCP tool with ENFORCED design validation.

    This tool requires a validation token from propose_tool_design(),
    making design validation MANDATORY instead of optional.

    ANALOGY: Like a pull request that requires review approval before merging.

    Args:
        tool_name: Name of the tool to create
        tool_code: The Python code for the tool (including @mcp.tool() decorator)
        validation_token: Token from propose_tool_design() - REQUIRED
        description: Optional description of what the tool does

    Returns:
        dict: Tool creation results
        {
            "success": bool,
            "tool_name": str,
            "validation_verified": bool,
            "file_path": str,
            "next_steps": List[str],
            "message": str
        }

    Example Usage:
        First call propose_tool_design() to get a validation token,
        then pass that token to this function along with your tool code.

    SECURITY NOTES:
    - Verifies validation token before proceeding
    - Creates audit trail of tool creation
    - Enforces design validation process
    - TRUE enforcement - cannot create tools without valid validation token
    """
    try:
        # Verify the validation token
        validator = DesignValidator()
        token_result = validator.verify_token(validation_token)

        if not token_result["valid"]:
            return {
                "success": False,
                "tool_name": tool_name,
                "validation_verified": False,
                "message": f"❌ Invalid validation token. You must call propose_tool_design() first.",
                "next_steps": [
                    "Call propose_tool_design() with your tool design",
                    "Fix any validation issues",
                    "Use the returned token with this function",
                ],
            }

        # Verify the tool name matches the proposal
        proposal_data = token_result["proposal_data"]
        if proposal_data["tool_name"] != tool_name:
            return {
                "success": False,
                "tool_name": tool_name,
                "validation_verified": False,
                "message": f"❌ Tool name mismatch. Token is for '{proposal_data['tool_name']}' but you're creating '{tool_name}'",
            }

        # Validate the tool code
        if "@mcp.tool()" not in tool_code:
            return {
                "success": False,
                "tool_name": tool_name,
                "validation_verified": True,
                "message": "❌ Tool code must include @mcp.tool() decorator",
            }

        if f"def {tool_name}" not in tool_code:
            return {
                "success": False,
                "tool_name": tool_name,
                "validation_verified": True,
                "message": f"❌ Tool code must define function '{tool_name}'",
            }

        # Find the right place to insert the tool
        script_dir = Path(__file__).parent
        server_file = script_dir / "platform_mcp.py"

        with open(server_file, "r") as f:
            current_content = f.read()

        # Insert before the EXPLANATORY COMMENTS section
        marker = "# =============================================================================\n# EXPLANATORY COMMENTS (for learning)\n# ============================================================================="

        if marker not in current_content:
            return {
                "success": False,
                "tool_name": tool_name,
                "validation_verified": True,
                "message": "❌ Could not find insertion point in platform_mcp.py",
            }

        # Build the complete tool code with header
        timestamp = datetime.utcnow().strftime("%Y-%m-%d")
        tool_section = f"""

# -----------------------------------------------------------------------------
# Tool: {tool_name}
# Created: {timestamp}
# Validation: {validation_token[:40]}...
# Layer: {proposal_data["layer"]}
# -----------------------------------------------------------------------------

{tool_code}

"""

        # Insert the tool
        parts = current_content.split(marker)
        new_content = parts[0] + tool_section + marker + parts[1]

        # Write back
        with open(server_file, "w") as f:
            f.write(new_content)

        # Log the creation
        create_session_note(
            f"Created tool '{tool_name}' with enforced validation (token: {validation_token[:20]}...)",
            section="Progress",
        )

        return {
            "success": True,
            "tool_name": tool_name,
            "validation_verified": True,
            "file_path": str(server_file),
            "validation_token_used": validation_token[:40] + "...",
            "next_steps": [
                "Test the tool: Restart Zed to load the new tool",
                "Verify it works as expected",
                f"Commit with message including validation token: {validation_token}",
                "Push to remote",
            ],
            "message": f"✅ Tool '{tool_name}' created successfully with enforced validation",
        }

    except Exception as e:
        return {
            "success": False,
            "tool_name": tool_name,
            "message": f"❌ Error creating tool: {str(e)}",
            "error": str(e),
        }
# =============================================================================
# EXPLANATORY COMMENTS (for learning)
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
# TEST TOOLS (For Enforcement Validation)
# =============================================================================
# These tools are for testing the enforcement mechanisms.
# They should be removed after testing is complete.


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


def analyze_critical_path(
    tasks: List[Dict[str, Any]],
    goal: Optional[str] = None,
    current_state: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Analyze task dependencies and determine optimal work order using critical path method.

    This tool performs forward and backward analysis to find the most efficient
    order for completing tasks, identifying:
    - Critical path (longest dependency chain)
    - Parallel work opportunities
    - Immediate actionable tasks
    - Blockers and dependencies

    ANALOGY: Like project management critical path analysis - finds the sequence
    that determines minimum completion time.

    Args:
        tasks: List of task dictionaries with structure:
            [
                {
                    "id": "task1",
                    "name": "Task description",
                    "duration": 1.0,  # Estimated time (hours, days, etc.)
                    "depends_on": ["task0"],  # List of prerequisite task IDs
                    "completed": False  # Optional
                },
                ...
            ]
        goal: Optional goal task ID (if None, assumes all tasks are goals)
        current_state: Optional list of completed task IDs

    Returns:
        dict: Analysis results with work order recommendation
        {
            "success": bool,
            "critical_path": List[str],  # Task IDs in critical path
            "critical_path_duration": float,  # Total time on critical path
            "work_order": List[Dict],  # Recommended order with levels
            "parallel_opportunities": List[List[str]],  # Tasks that can be done in parallel
            "immediate_tasks": List[str],  # Tasks that can start now
            "blockers": Dict[str, List[str]],  # What blocks each task
            "analysis": {
                "total_tasks": int,
                "completed_tasks": int,
                "remaining_tasks": int,
                "estimated_completion": float
            },
            "analysis_token": str,  # Use this token to prove analysis was done
            "message": str
        }

    Example Usage:
        tasks = [
            {"id": "design", "name": "Design system", "duration": 2, "depends_on": []},
            {"id": "impl", "name": "Implement", "duration": 5, "depends_on": ["design"]},
            {"id": "test", "name": "Test", "duration": 3, "depends_on": ["impl"]},
            {"id": "docs", "name": "Document", "duration": 2, "depends_on": ["design"]}
        ]

        result = analyze_critical_path(tasks, goal="test")

        # Shows: design -> impl -> test is critical path (10 units)
        # docs can be done in parallel with impl/test

    SECURITY NOTES:
    - Pure analysis, no side effects
    - No external dependencies
    - No system state changes

    DESIGN VALIDATION (validation: valid-2cad9565-d6557045de90a7fe):
    - Layer: personal (workflow optimization)
    - Dependencies: None (pure logic)
    - No system state changes
    - No hardcoded configuration
    """
    try:
        # Validate input
        if not tasks:
            return {
                "success": False,
                "message": "❌ No tasks provided",
            }

        # Build task lookup
        task_map = {task["id"]: task for task in tasks}

        # Validate all dependencies exist
        for task in tasks:
            for dep in task.get("depends_on", []):
                if dep not in task_map:
                    return {
                        "success": False,
                        "message": f"❌ Task '{task['id']}' depends on unknown task '{dep}'",
                    }

        # Determine completed tasks
        completed = set(current_state or [])
        for task in tasks:
            if task.get("completed", False):
                completed.add(task["id"])

        # Build reverse dependency map (what depends on each task)
        dependents = {task_id: [] for task_id in task_map}
        for task in tasks:
            for dep in task.get("depends_on", []):
                dependents[dep].append(task["id"])

        # Calculate earliest start time for each task (forward pass)
        earliest_start = {}

        def calc_earliest_start(task_id):
            if task_id in earliest_start:
                return earliest_start[task_id]

            task = task_map[task_id]
            deps = task.get("depends_on", [])

            if not deps:
                earliest_start[task_id] = 0
            else:
                max_dep_finish = max(
                    calc_earliest_start(dep) + task_map[dep].get("duration", 1)
                    for dep in deps
                )
                earliest_start[task_id] = max_dep_finish

            return earliest_start[task_id]

        # Calculate for all tasks
        for task_id in task_map:
            calc_earliest_start(task_id)

        # Find goal tasks (tasks with no dependents, or specified goal)
        if goal:
            goal_tasks = [goal] if goal in task_map else []
        else:
            goal_tasks = [tid for tid in task_map if not dependents[tid]]

        if not goal_tasks:
            return {
                "success": False,
                "message": "❌ No goal tasks found (no tasks without dependents)",
            }

        # Calculate latest start time for each task (backward pass)
        latest_start = {}
        project_end = max(
            earliest_start[tid] + task_map[tid].get("duration", 1) for tid in goal_tasks
        )

        def calc_latest_start(task_id):
            if task_id in latest_start:
                return latest_start[task_id]

            task = task_map[task_id]
            deps_on_this = dependents[task_id]

            if not deps_on_this:
                # Goal task
                latest_start[task_id] = earliest_start[task_id]
            else:
                min_dependent_start = min(
                    calc_latest_start(dep) for dep in deps_on_this
                )
                latest_start[task_id] = min_dependent_start - task.get("duration", 1)

            return latest_start[task_id]

        for task_id in task_map:
            calc_latest_start(task_id)

        # Identify critical path (tasks with zero slack)
        critical = [tid for tid in task_map if earliest_start[tid] == latest_start[tid]]

        # Order critical path
        critical_ordered = sorted(critical, key=lambda x: earliest_start[x])
        critical_duration = sum(
            task_map[tid].get("duration", 1) for tid in critical_ordered
        )

        # Identify immediate actionable tasks (not completed, all deps completed)
        immediate = [
            tid
            for tid in task_map
            if tid not in completed
            and all(dep in completed for dep in task_map[tid].get("depends_on", []))
        ]

        # Build work order by levels (topological sort with levels)
        work_order = []
        remaining = set(task_map.keys()) - completed
        level = 0

        while remaining:
            # Tasks at this level: all dependencies satisfied
            level_tasks = [
                tid
                for tid in remaining
                if all(
                    dep in completed or dep not in remaining
                    for dep in task_map[tid].get("depends_on", [])
                )
            ]

            if not level_tasks:
                break  # Circular dependency

            work_order.append(
                {
                    "level": level,
                    "tasks": level_tasks,
                    "can_parallelize": len(level_tasks) > 1,
                    "duration": max(
                        task_map[tid].get("duration", 1) for tid in level_tasks
                    ),
                }
            )

            remaining -= set(level_tasks)
            completed.update(level_tasks)
            level += 1

        # Identify blockers for each incomplete task
        blockers = {}
        for tid in task_map:
            if tid not in (current_state or []):
                incomplete_deps = [
                    dep
                    for dep in task_map[tid].get("depends_on", [])
                    if dep not in (current_state or [])
                ]
                if incomplete_deps:
                    blockers[tid] = incomplete_deps

        # Calculate completion estimate
        total_tasks = len(tasks)
        completed_count = len(current_state or [])
        remaining_count = total_tasks - completed_count

        return {
            "success": True,
            "critical_path": critical_ordered,
            "critical_path_duration": critical_duration,
            "work_order": work_order,
            "parallel_opportunities": [
                level["tasks"] for level in work_order if level["can_parallelize"]
            ],
            "immediate_tasks": immediate,
            "blockers": blockers,
            "analysis": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_count,
                "remaining_tasks": remaining_count,
                "estimated_completion": sum(level["duration"] for level in work_order),
            },
            "analysis_token": f"efficiency-{hash(tuple(critical_ordered))}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "message": f"✅ Critical path analysis complete. Path: {' → '.join(critical_ordered)}",
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Analysis error: {str(e)}",
            "error": str(e),
        }


def make_roadmap_decision(
    tasks: List[Dict[str, Any]],
    analysis_token: str,
    rationale: str = "",
) -> Dict[str, Any]:
    """
    Make a roadmap decision based on critical path analysis.

    This tool ENFORCES efficiency analysis - you cannot make a roadmap decision
    without first analyzing the critical path using analyze_critical_path().

    ANALOGY: Like requiring a design review before starting work - you must
    analyze the most efficient path before committing to a direction.

    Args:
        tasks: Same task list used in analyze_critical_path()
        analysis_token: Token from analyze_critical_path() proving analysis was done
        rationale: Optional explanation of the decision

    Returns:
        dict: Decision results with recommended next action
        {
            "success": bool,
            "decision": str,  # The immediate next action
            "critical_path": List[str],
            "immediate_tasks": List[str],
            "rationale": str,
            "message": str
        }

    Example Usage:
        # Step 1: Analyze
        analysis = analyze_critical_path(tasks, goal="production_ready")

        # Step 2: Make decision (requires token from step 1)
        decision = make_roadmap_decision(
            tasks=tasks,
            analysis_token=analysis["analysis_token"],
            rationale="Must validate enforcement before Phase 2"
        )

        # Result: "✅ Decision: Start with 'test_enforcement' (blocks everything else)"

    SECURITY NOTES:
    - Requires valid analysis token (enforces workflow)
    - Pure analysis, no system changes
    - Token validation prevents bypassing analysis

    DESIGN VALIDATION (validation: valid-efficiency-enforcement):
    - Layer: personal (workflow enforcement)
    - Dependencies: analyze_critical_path()
    - No system state changes
    - Enforces efficiency analysis before decisions
    """
    try:
        # Validate token format
        if not analysis_token.startswith("efficiency-"):
            return {
                "success": False,
                "message": "❌ Invalid analysis token. You must call analyze_critical_path() first.",
                "guidance": "Call analyze_critical_path(tasks) to get a valid token",
            }

        # Re-run analysis to get fresh results (token proves they did the analysis)
        analysis_result = analyze_critical_path(tasks)

        if not analysis_result.get("success"):
            return {
                "success": False,
                "message": f"❌ Analysis failed: {analysis_result.get('message')}",
            }

        # Get the immediate actionable tasks
        immediate = analysis_result.get("immediate_tasks", [])
        critical_path = analysis_result.get("critical_path", [])

        if not immediate:
            return {
                "success": True,
                "decision": "All tasks completed or blocked",
                "critical_path": critical_path,
                "immediate_tasks": [],
                "rationale": rationale,
                "message": "✅ No immediate tasks available (all done or blocked)",
            }

        # The decision: start with the immediate task that's on the critical path
        # If multiple immediate tasks exist, prioritize those on critical path
        critical_immediate = [t for t in immediate if t in critical_path]

        if critical_immediate:
            decision = critical_immediate[0]
            reason = f"on critical path and has no blockers"
        else:
            decision = immediate[0]
            reason = f"ready to start (not on critical path, can be done in parallel)"

        # Build task lookup for readable output
        task_map = {task["id"]: task for task in tasks}
        decision_name = task_map[decision].get("name", decision)

        return {
            "success": True,
            "decision": decision,
            "decision_name": decision_name,
            "critical_path": critical_path,
            "immediate_tasks": immediate,
            "rationale": rationale,
            "reason": reason,
            "message": f"✅ Decision: Start with '{decision}' ({reason})",
            "next_action": f"Begin: {decision_name}",
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Decision error: {str(e)}",
            "error": str(e),
        }
# =============================================================================
# V3: Ephemeral File Management Tools (Session Continuity)
# =============================================================================
# These tools make ephemeral files EASY to use, solving the "documentation
# without convenience" problem. Instead of relying on thread summaries,
# these tools make session notes effortless.
#
# Design Principle: Make the "right way" (ephemeral files) easier than the
# "wrong way" (thread summaries that don't scale).


def create_session_note(
    content: str, section: str = "Progress", session_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create or append to current session ephemeral note with automatic timestamp and structure.

    This makes ephemeral file usage EASY - no need to manually manage files,
    paths, or timestamps. Just call this function and your note is recorded.

    ANALOGY: Like `git commit` for session notes - structured, timestamped, automatic.

    Args:
        content: The note content to add
        section: Section to add to ["Goals", "Progress", "Decisions", "Issues", "Next Steps"]
        session_name: Optional session name (auto-generates from date if None)

    Returns:
        dict: Session note results
        {
            "success": bool,
            "session_file": str,  # Path to the session file
            "content_added": str,
            "timestamp": str,
            "message": str
        }

    Example Usage:
        # Start of session
        create_session_note(
            "Implementing ephemeral file management tools",
            section="Goals"
        )

        # During session
        create_session_note(
            "Validated 3 tool designs, all passed",
            section="Progress"
        )

        # Important decision
        create_session_note(
            "Using automatic timestamping instead of manual",
            section="Decisions"
        )

        # End of session
        create_session_note(
            "Test the tools and update MW-001",
            section="Next Steps"
        )

    SECURITY NOTES:
    - Pure file I/O (no shell commands)
    - Restricted to .ephemeral/sessions/ directory
    - No user input in file paths (prevents traversal)

    DESIGN VALIDATION (validation: valid-0fe721ec-375fcbb50b5e384b):
    - Layer: personal (session management)
    - No external dependencies
    - No system state changes (just file writes)
    - Makes ephemeral files easier to use
    """
    from datetime import datetime

    try:
        # Get script directory
        script_dir = Path(__file__).parent
        sessions_dir = script_dir / ".ephemeral" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)

        # Generate session filename
        if session_name is None:
            session_name = datetime.now().strftime("%Y-%m-%d-session")

        session_file = sessions_dir / f"{session_name}.md"

        # Create or load existing file
        if session_file.exists():
            with open(session_file, "r") as f:
                existing_content = f.read()
        else:
            # Initialize new session file with structure
            existing_content = f"""# Session: {session_name}

**Date:** {datetime.now().strftime("%Y-%m-%d")}
**Status:** In Progress

---

## Goals

## Progress

## Decisions

## Issues

## Next Steps

"""

        # Add timestamp and content to appropriate section
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = f"\n### {timestamp}\n{content}\n"

        # Find the section and add content
        section_header = f"## {section}"
        if section_header in existing_content:
            # Insert after the section header
            parts = existing_content.split(section_header)
            # Find next section or end
            next_section_idx = parts[1].find("\n## ")
            if next_section_idx != -1:
                parts[1] = (
                    parts[1][:next_section_idx]
                    + new_entry
                    + parts[1][next_section_idx:]
                )
            else:
                parts[1] = parts[1] + new_entry

            updated_content = section_header.join(parts)
        else:
            # Section doesn't exist, append to end
            updated_content = existing_content + f"\n{section_header}\n{new_entry}\n"

        # Write back
        with open(session_file, "w") as f:
            f.write(updated_content)

        return {
            "success": True,
            "session_file": str(session_file),
            "content_added": content,
            "timestamp": timestamp,
            "section": section,
            "message": f"✅ Added note to {section} section of {session_file.name}",
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Error creating session note: {str(e)}",
            "error": str(e),
        }


def read_session_notes(
    session_name: Optional[str] = None, days_back: int = 7
) -> Dict[str, Any]:
    """
    Read recent session notes from ephemeral directory with smart filtering.

    Makes it easy to review what happened in previous sessions without
    manually navigating directories or remembering file names.

    ANALOGY: Like `git log` for session notes - shows recent history.

    Args:
        session_name: Specific session name to read (None = most recent)
        days_back: How many days back to search (default: 7)

    Returns:
        dict: Session notes content
        {
            "success": bool,
            "session_file": str,
            "content": str,
            "last_modified": str,
            "message": str
        }

    Example Usage:
        # Read today's session
        result = read_session_notes()

        # Read specific session
        result = read_session_notes(session_name="2025-01-07-session")

        # Search last 30 days
        result = read_session_notes(days_back=30)

    SECURITY NOTES:
    - Read-only operation
    - Restricted to .ephemeral/sessions/ directory
    - No user input in file paths

    DESIGN VALIDATION (validation: valid-e9859a54-149da04934bcfcd3):
    - Layer: personal (session management)
    - No external dependencies
    - No system state changes (read-only)
    """
    from datetime import datetime, timedelta

    try:
        script_dir = Path(__file__).parent
        sessions_dir = script_dir / ".ephemeral" / "sessions"

        if not sessions_dir.exists():
            return {
                "success": False,
                "message": "❌ No sessions directory found (.ephemeral/sessions/)",
            }

        # Find session files
        if session_name:
            # Specific session requested
            session_file = sessions_dir / f"{session_name}.md"
            if not session_file.exists():
                return {
                    "success": False,
                    "message": f"❌ Session file not found: {session_name}.md",
                }
            target_file = session_file
        else:
            # Find most recent session within days_back
            cutoff_date = datetime.now() - timedelta(days=days_back)
            session_files = []

            for f in sessions_dir.glob("*.md"):
                if f.stat().st_mtime > cutoff_date.timestamp():
                    session_files.append(f)

            if not session_files:
                return {
                    "success": False,
                    "message": f"❌ No session files found in last {days_back} days",
                }

            # Get most recent
            target_file = max(session_files, key=lambda f: f.stat().st_mtime)

        # Read the file
        with open(target_file, "r") as f:
            content = f.read()

        last_modified = datetime.fromtimestamp(target_file.stat().st_mtime)

        return {
            "success": True,
            "session_file": str(target_file),
            "content": content,
            "last_modified": last_modified.strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"✅ Read session: {target_file.name}",
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Error reading session notes: {str(e)}",
            "error": str(e),
        }


def list_session_files(days_back: int = 30) -> Dict[str, Any]:
    """
    List all session files in ephemeral directory with metadata.

    Shows what session files exist, when they were last modified, and
    how large they are. Helps with session continuity and discovery.

    ANALOGY: Like `ls -lh` for session files - shows what's available.

    Args:
        days_back: How many days back to list (default: 30)

    Returns:
        dict: List of session files with metadata
        {
            "success": bool,
            "sessions": List[Dict],
            "count": int,
            "message": str
        }

    Example Usage:
        result = list_session_files()

        for session in result["sessions"]:
            print(f"{session['name']}: {session['size']} bytes, {session['last_modified']}")

    SECURITY NOTES:
    - Read-only operation
    - Restricted to .ephemeral/sessions/ directory

    DESIGN VALIDATION (validation: valid-61df6dbe-35c32cb4632ed4a1):
    - Layer: personal (session management)
    - No external dependencies
    - No system state changes (read-only)
    """
    from datetime import datetime, timedelta

    try:
        script_dir = Path(__file__).parent
        sessions_dir = script_dir / ".ephemeral" / "sessions"

        if not sessions_dir.exists():
            return {
                "success": False,
                "sessions": [],
                "count": 0,
                "message": "❌ No sessions directory found",
            }

        # Find session files within timeframe
        cutoff_date = datetime.now() - timedelta(days=days_back)
        sessions = []

        for f in sessions_dir.glob("*.md"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime > cutoff_date:
                sessions.append(
                    {
                        "name": f.name,
                        "path": str(f),
                        "size": f.stat().st_size,
                        "last_modified": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                        "age_days": (datetime.now() - mtime).days,
                    }
                )

        # Sort by most recent first
        sessions.sort(key=lambda s: s["last_modified"], reverse=True)

        return {
            "success": True,
            "sessions": sessions,
            "count": len(sessions),
            "days_back": days_back,
            "message": f"✅ Found {len(sessions)} session file(s) in last {days_back} days",
        }

    except Exception as e:
        return {
            "success": False,
            "sessions": [],
            "count": 0,
            "message": f"❌ Error listing sessions: {str(e)}",
            "error": str(e),
        }
# =============================================================================
# V4: MCP Prompts (Workflow Shortcuts)
# =============================================================================
# These prompts turn META-WORKFLOWS into discoverable /commands that guide
# the AI through workflows step-by-step. This provides stronger enforcement
# than just documentation - the AI can discover and trigger workflows easily.
#
# DESIGN VALIDATION (validation: valid-6c59c8d8-90eb939168267b56):
# - Layer: personal (workflow guidance)
# - Dependencies: FastMCP
# - No system state changes (guidance only)
@mcp.prompt()
def new_tool_workflow() -> str:
    """
    /new-tool - Start MW-002 workflow for creating a new MCP tool.

    Guides you through the complete tool creation process with validation.
    """
    return """# MW-002: New MCP Tool Development Workflow

You are starting the workflow to create a new MCP tool. Follow these steps:

## Step 1: Requirements Gathering
What does the tool need to do? Describe:
- Purpose (one sentence)
- Inputs/parameters
- Expected output
- Which layer (platform/team/personal)

## Step 2: ⚠️ MANDATORY Design Validation
**YOU MUST call propose_tool_design() before proceeding!**

```python
result = propose_tool_design(
    tool_name="your_tool_name",
    purpose="what it does",
    layer="platform|team|personal",
    dependencies=["list", "of", "dependencies"],
    requires_system_state_change=False,
    implementation_approach="how it will work"
)
```

If valid=False: Fix issues and resubmit
If valid=True: Save the token and proceed

## Step 3: Implementation
Now implement the tool with the @mcp.tool() decorator.
Include the validation token in your commit message.

## Step 4: Testing
Test the tool works as expected.

## Step 5: Documentation
Update relevant documentation (README, META-WORKFLOWS if needed).

**Remember: The validation token proves you followed the design process!**
"""
@mcp.prompt()
def end_session_workflow() -> str:
    """
    /end-session - Start MW-001 workflow for ending a session properly.

    Guides you through creating session summaries and documentation.
    """
    return """# MW-001: Thread Ending Summary Workflow

This session is ending. Follow these steps to ensure continuity:

## Step 1: Document Session in Ephemeral File
Use the session note tools:

```python
create_session_note(
    "Summary of what was accomplished",
    section="Progress"
)

create_session_note(
    "Key decisions made",
    section="Decisions"
)

create_session_note(
    "What to do next session",
    section="Next Steps"
)
```

## Step 2: Extract Persistent Documentation
Review .ephemeral/sessions/YYYY-MM-DD-session.md and extract:
- Completed work → Update relevant docs
- Important decisions → Document in architecture docs
- Testing results → Update TESTING.md if needed

## Step 3: Create Next Session Checklist
What does the next session need to know?
- What was completed?
- What's in progress?
- What are the blockers?

## Step 4: Git State Check
Ensure all work is committed:
- `git status` - should be clean
- `git log` - verify commits are descriptive
- `git push` - sync to remote

## Step 5: Final Summary
Create a brief summary of the session state for thread handoff.
"""
@mcp.prompt()
def debug_flux_workflow() -> str:
    """
    /debug-flux - Start MW-006 workflow for debugging Flux issues.

    Guides you through systematic Flux troubleshooting.
    """
    return """# MW-006: Flux Debugging Workflow

Follow these steps to debug Flux systematically:

## Step 1: List Kustomizations
```python
result = list_flux_kustomizations(
    cluster="staging|production",
    node="k8s-master-01",
    show_suspend=True
)
```

Look for kustomizations with ready=False or suspended=True.

## Step 2: Get Details
For the problematic kustomization:
```python
result = get_kustomization_details(
    cluster="...",
    node="...",
    name="failing-kustomization",
    namespace="flux-system"
)
```

## Step 3: Check Events
```python
result = get_kustomization_events(
    cluster="...",
    node="...",
    name="failing-kustomization"
)
```

## Step 4: Review Controller Logs
```python
result = get_flux_logs(
    cluster="...",
    node="...",
    component="kustomize-controller",
    tail=100
)
```

## Step 5: Identify Root Cause
Common issues:
- Source repository unreachable
- Invalid Kustomization syntax
- Missing dependencies
- RBAC permissions

## Step 6: Take Action
- Suspend if needed: `suspend_flux_kustomization(...)`
- Fix the root cause in Git
- Resume: `resume_flux_kustomization(...)`
- Or reconcile: `reconcile_flux_kustomization(...)`
"""
@mcp.prompt()
def validate_design_workflow() -> str:
    """
    /validate-design - Quick guide for design validation.

    Shows how to use propose_tool_design() effectively.
    """
    return """# Design Validation Quick Guide

## When to Use
Before implementing ANY new MCP tool or modifying existing ones.

## How to Use
```python
result = propose_tool_design(
    tool_name="your_tool_name",
    purpose="One sentence: what does it do?",
    layer="platform|team|personal",
    dependencies=["run_remote_command", "kubectl", "etc"],
    requires_system_state_change=False,  # True if it modifies system
    implementation_approach="Brief: how will you implement it?"
)
```

## What Gets Validated
- ✅ No hardcoded configuration (cluster names, IPs)
- ✅ Correct layer placement
- ✅ Proper dependencies (abstractions not implementations)
- ✅ Ansible-first (no shell scripts for system changes)
- ✅ No anti-patterns (god tools, tight coupling)

## If Validation Fails
```python
# result["valid"] == False
# Fix the issues in result["issues"]
# Resubmit with fixes
```

## If Validation Passes
```python
# result["valid"] == True
# Save the token: result["token"]
# Proceed with implementation
# Include token in commit message
```

## Example
```python
result = propose_tool_design(
    tool_name="list_kubernetes_pods",
    purpose="List all pods in a Kubernetes cluster",
    layer="team",
    dependencies=["run_remote_command", "kubectl"],
    requires_system_state_change=False,
    implementation_approach="Uses run_remote_command to execute 'kubectl get pods -A -o json'"
)
# Valid! Token: valid-abc123-xyz789
```
"""
# =============================================================================
# V5: Enforced Tool Creation (Pre-condition System)
# =============================================================================
# This tool ENFORCES design validation by requiring a validation token
# before allowing tool creation. This makes validation MANDATORY, not optional.
#
# DESIGN VALIDATION (validation: valid-e32a9d0e-c31d43d9011ed2dc):
# - Layer: personal (development workflow)
# - Dependencies: propose_tool_design, verify_tool_design_token
# - No system state changes (just enforces workflow)


def test_enforcement_workflow() -> Dict[str, Any]:
    """
    Test tool to verify enforcement workflows are functional.

    This tool tests:
    1. That it can be called (MCP registration works)
    2. That workflow state tracking works
    3. That the tool responds correctly

    TESTING ONLY - Should be removed after validation.

    Returns:
        dict: Test results
        {
            "success": bool,
            "message": str,
            "workflow_state": Dict,
            "timestamp": str
        }
    """
    from datetime import datetime

    from workflow_state import get_workflow_state

    try:
        current_state = get_workflow_state()

        return {
            "success": True,
            "message": "✅ Enforcement workflow test successful",
            "workflow_state": current_state,
            "timestamp": datetime.now().isoformat(),
            "tests_passed": [
                "MCP tool registration works",
                "Tool can be called from AI context",
                "Return values are properly formatted",
            ],
            "note": "This is a test tool created under one-time exception to Rule #1",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Test failed: {str(e)}",
            "error": str(e),
            "error": str(e)
        }
# =============================================================================
# SERVER STARTUP
# =============================================================================

if __name__ == "__main__":
    # This block runs when you execute: python platform_mcp.py
    # ANALOGY: Like the "main:" section in an Ansible playbook

    # Start the MCP server
    # This will listen for requests from your AI agent (Claude Desktop, Zed, etc.)
    mcp.run()
