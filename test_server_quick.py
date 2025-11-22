#!/usr/bin/env python3
"""
Quick test to verify MCP server can start and list tools.
This version exits immediately after testing.
"""
import sys
import subprocess
import json
import time

def test_server():
    """Test that the server starts and can list tools."""
    print("🔍 Quick MCP Server Test")
    print("=" * 40)
    
    # Use the current Python interpreter
    command = [sys.executable, "platform_mcp.py"]
    
    try:
        # Start the server
        print("1️⃣  Starting MCP server...")
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Give it a moment to start
        time.sleep(1)
        
        # Send initialize request
        print("2️⃣  Initializing connection...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "quick-test", "version": "1.0.0"}
            }
        }
        
        request_str = json.dumps(init_request) + "\n"
        process.stdin.write(request_str)
        process.stdin.flush()
        
        # Read response
        response_str = process.stdout.readline()
        if response_str:
            response = json.loads(response_str.strip())
            server_name = response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')
            print(f"✅ Connected to: {server_name}")
        else:
            print("❌ No response from server")
            return False
            
        # List tools
        print("3️⃣  Listing tools...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        request_str = json.dumps(tools_request) + "\n"
        process.stdin.write(request_str)
        process.stdin.flush()
        
        response_str = process.stdout.readline()
        if response_str:
            response = json.loads(response_str.strip())
            tools = response.get('result', {}).get('tools', [])
            print(f"✅ Found {len(tools)} tools")
            
            # Show first few tools
            for i, tool in enumerate(tools[:3]):
                print(f"   • {tool['name']}")
            if len(tools) > 3:
                print(f"   • ... and {len(tools) - 3} more")
        else:
            print("❌ No tools response")
            return False
            
        print("\n✅ Server is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        # Always cleanup
        if 'process' in locals():
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
        print("🧹 Server stopped")

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
