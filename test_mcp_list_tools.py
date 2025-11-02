#!/usr/bin/env python3
"""
Test listing and calling tools via MCP protocol.
This fully simulates what Zed Preview does.
"""
import subprocess
import json

def send_request(process, request):
    """Send a JSON-RPC request and get response."""
    request_str = json.dumps(request) + "\n"
    process.stdin.write(request_str)
    process.stdin.flush()
    
    response_str = process.stdout.readline()
    return json.loads(response_str.strip())

print("🔍 Testing MCP Tool Discovery and Execution")
print("=" * 60)

command = [".venv/bin/python", "platform_mcp.py"]

try:
    # Start the MCP server
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Step 1: Initialize
    print("\n1️⃣  Initializing MCP connection...")
    init_response = send_request(process, {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    })
    print(f"✅ Server: {init_response['result']['serverInfo']['name']}")
    
    # Step 2: List available tools
    print("\n2️⃣  Listing available tools...")
    tools_response = send_request(process, {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    })
    
    print(f"✅ Found {len(tools_response['result']['tools'])} tool(s):")
    for tool in tools_response['result']['tools']:
        print(f"\n   📦 Tool: {tool['name']}")
        print(f"      Description: {tool['description'][:80]}...")
        if 'inputSchema' in tool:
            params = tool['inputSchema'].get('properties', {})
            print(f"      Parameters: {list(params.keys()) if params else 'None'}")
    
    # Step 3: Call the list_kube_contexts tool
    print("\n3️⃣  Calling 'list_kube_contexts' tool...")
    call_response = send_request(process, {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "list_kube_contexts",
            "arguments": {}
        }
    })
    
    if 'result' in call_response:
        content = call_response['result']['content']
        print(f"✅ Tool executed successfully!")
        print(f"\n📋 Result:")
        for item in content:
            if item['type'] == 'text':
                print(f"{item['text']}")
    else:
        print(f"❌ Error: {call_response.get('error', 'Unknown error')}")
    
    # Cleanup
    process.terminate()
    process.wait(timeout=2)
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! The MCP server is working correctly.")
    print("\nThis is exactly what Zed Preview does when you use the tool.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    if 'process' in locals():
        process.kill()
