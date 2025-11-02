#!/usr/bin/env python3
"""
Test the Teleport V1a tools directly.
"""
import json
from platform_mcp import (
    check_tsh_installed,
    get_tsh_client_version,
    get_teleport_proxy_version,
    verify_teleport_compatibility,
)

print("=" * 70)
print("Testing Teleport V1a Tools")
print("=" * 70)

print("\n1️⃣  Testing check_tsh_installed()")
print("-" * 70)
result = check_tsh_installed()
print(json.dumps(result, indent=2))

print("\n2️⃣  Testing get_tsh_client_version()")
print("-" * 70)
result = get_tsh_client_version()
print(json.dumps(result, indent=2))

print("\n3️⃣  Testing get_teleport_proxy_version('staging')")
print("-" * 70)
result = get_teleport_proxy_version("staging")
print(json.dumps(result, indent=2))

print("\n4️⃣  Testing verify_teleport_compatibility()")
print("-" * 70)
result = verify_teleport_compatibility()
print(json.dumps(result, indent=2))

print("\n" + "=" * 70)
print("✅ All tests complete!")
print("=" * 70)
