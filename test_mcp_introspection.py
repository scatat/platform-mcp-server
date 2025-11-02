#!/usr/bin/env python3
"""
Test MCP server introspection - verify the server registers tools correctly.
"""
from platform_mcp import mcp

print("🔍 Inspecting MCP Server...")
print(f"Server name: {mcp.name}")

print("\n📋 Registered Tools:")
# FastMCP stores tools in an internal registry
# Let's see what we can access
print(f"  Total tools: {len(mcp._tool_manager._tools)}")

for tool_name, tool_info in mcp._tool_manager._tools.items():
    print(f"\n  Tool: {tool_name}")
    print(f"    Description: {tool_info.description[:100]}...")
    print(f"    Function: {tool_info.fn.__name__}")
    
print("\n✅ MCP Server introspection complete!")
