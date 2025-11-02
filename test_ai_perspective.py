#!/usr/bin/env python3
"""
Simulate what an AI agent sees when discovering and calling tools.
This mimics the MCP protocol's tool discovery and execution flow.
"""
from platform_mcp import mcp, list_kube_contexts
import inspect

print("🤖 AI Agent Perspective: Tool Discovery\n")
print("=" * 60)

# Step 1: Tool Discovery (what the AI agent sees in the manifest)
print("\n1️⃣  TOOL MANIFEST (What the AI discovers)")
print("=" * 60)

tool_info = mcp._tool_manager._tools.get('list_kube_contexts')
if tool_info:
    print(f"Tool Name: {tool_info.name}")
    print(f"\nDescription (the AI's instruction manual):")
    print(f"{tool_info.description}")
    
    # Show the function signature (type hints)
    sig = inspect.signature(tool_info.fn)
    print(f"\nFunction Signature: {tool_info.fn.__name__}{sig}")
    print(f"Return Type: {sig.return_annotation}")

# Step 2: Tool Execution (AI calls the tool)
print("\n\n2️⃣  TOOL EXECUTION (AI calls the tool)")
print("=" * 60)
print("AI Decision: 'The user wants to see their Kubernetes contexts.'")
print("AI Action: Calling list_kube_contexts()")
print("\nExecuting...")

result = list_kube_contexts()

print("\n3️⃣  TOOL RESPONSE (What the AI receives)")
print("=" * 60)
print(f"Type: {type(result).__name__}")
print(f"Content:\n{result}")

# Step 3: AI interprets the result
print("\n\n4️⃣  AI INTERPRETATION")
print("=" * 60)
contexts = result.splitlines()
print(f"AI Understanding: 'The user has {len(contexts)} Kubernetes contexts available:'")
for i, ctx in enumerate(contexts, 1):
    print(f"  {i}. {ctx}")

print("\n✅ Complete! This is exactly how your AI agent will use this tool.")
