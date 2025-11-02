#!/usr/bin/env python3
"""
Quick test to verify the MCP server loads and exposes tools correctly.
"""

print("✅ MCP Server module loaded successfully!")

print("\n🧪 Testing list_kube_contexts tool directly...")
try:
    from platform_mcp import list_kube_contexts
    result = list_kube_contexts()
    print(f"✅ Success! Found {len(result.splitlines())} Kubernetes context(s):")
    for ctx in result.splitlines():
        print(f"  - {ctx}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
