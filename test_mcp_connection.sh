#!/bin/bash
# Test the MCP server using the MCP Inspector
# This simulates how Zed Preview connects to the server

echo "🔍 Testing MCP Server Connection..."
echo ""
echo "Command: $(pwd)/.venv/bin/python platform_mcp.py"
echo ""

# Use npx to run the MCP inspector
npx @modelcontextprotocol/inspector \
  $(pwd)/.venv/bin/python \
  $(pwd)/platform_mcp.py
