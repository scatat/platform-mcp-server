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

import subprocess  # For running shell commands safely (like calling `kubectl`)
import os          # For environment variables and path operations
import shlex       # For safely parsing command strings (prevents injection!)
from typing import List  # Type hints - tells us what data type to expect

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
            shell=False,           # CRITICAL: Never use shell=True with user input!
            capture_output=True,   # Capture stdout and stderr
            text=True,             # Return strings, not bytes
            check=True             # Raise exception if command fails
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
