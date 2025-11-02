#!/usr/bin/env python3
"""
Test the MCP server by simulating the protocol communication.
This tests what Zed Preview does when it connects to the MCP server.
"""
import subprocess
import json

print("🔍 Testing MCP Server Protocol Communication")
print("=" * 60)

# The command Zed Preview runs
command = [
    ".venv/bin/python",
    "platform_mcp.py"
]

print(f"\nCommand: {' '.join(command)}")
print("\nStarting MCP server and sending 'initialize' request...")

# Simulate the MCP protocol initialization
initialize_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    }
}

try:
    # Start the MCP server process
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send the initialize request
    request_str = json.dumps(initialize_request) + "\n"
    stdout, stderr = process.communicate(input=request_str, timeout=5)
    
    print("\n📤 Sent initialize request")
    print(f"📥 Response received:")
    
    if stdout:
        try:
            response = json.loads(stdout.strip())
            print(json.dumps(response, indent=2))
            
            # Check if tools are listed
            if "result" in response and "capabilities" in response["result"]:
                print("\n✅ MCP server responded successfully!")
                print("\nCapabilities:")
                print(json.dumps(response["result"]["capabilities"], indent=2))
            else:
                print("\n⚠️  Response doesn't match expected format")
        except json.JSONDecodeError:
            print(f"Raw output: {stdout}")
    
    if stderr:
        print(f"\n⚠️  Stderr: {stderr}")
    
    process.terminate()
    
except subprocess.TimeoutExpired:
    print("\n❌ Server timed out")
    process.kill()
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete!")
