#!/usr/bin/env python3
"""
Test script for V1b Teleport SSH & Remote Command Execution Tools

This script tests the new V1b tools that handle SSH-based remote command
execution via Teleport. This is the REAL platform engineering workflow!

Run this after implementing V1b tools to verify they work correctly.

Usage:
    python test_teleport_v1b.py
"""

import sys

from platform_mcp import (
    list_flux_kustomizations,
    list_teleport_nodes,
    reconcile_flux_kustomization,
    run_remote_command,
    verify_ssh_access,
)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(result, indent=0):
    """Pretty-print a result dictionary."""
    indent_str = "  " * indent
    for key, value in result.items():
        if isinstance(value, dict):
            print(f"{indent_str}{key}:")
            print_result(value, indent + 1)
        elif isinstance(value, list):
            print(f"{indent_str}{key}:")
            if not value:
                print(f"{indent_str}  (empty)")
            else:
                for item in value:
                    if isinstance(item, dict):
                        print_result(item, indent + 1)
                        print()
                    else:
                        print(f"{indent_str}  - {item}")
        else:
            # Truncate long strings
            if isinstance(value, str) and len(value) > 200:
                print(f"{indent_str}{key}: {value[:200]}... (truncated)")
            else:
                print(f"{indent_str}{key}: {value}")


def test_list_nodes():
    """Test 1: List available nodes in Teleport clusters."""
    print_section("TEST 1: List Teleport Nodes")

    clusters = ["staging", "production"]
    results = {}

    for cluster in clusters:
        print(f"\nTesting: list_teleport_nodes('{cluster}')")
        print(f"Expected: Show SSH nodes in {cluster}\n")

        result = list_teleport_nodes(cluster)
        print_result(result)
        results[cluster] = result
        print("\n" + "-" * 80)

    # Also test with filter
    print(f"\nTesting: list_teleport_nodes('staging', filter='k8s')")
    print("Expected: Show only k8s nodes\n")
    result = list_teleport_nodes("staging", filter="k8s")
    print_result(result)
    results["staging_k8s"] = result

    return results


def test_verify_access(cluster, node):
    """Test 2: Verify SSH access to a specific node."""
    print_section(f"TEST 2: Verify SSH Access to {node}")
    print(f"Testing: verify_ssh_access('{cluster}', '{node}')")
    print("Expected: Confirm SSH connection works\n")

    result = verify_ssh_access(cluster, node, user="root")
    print_result(result)

    return result


def test_run_command(cluster, node):
    """Test 3: Run a simple remote command."""
    print_section(f"TEST 3: Run Remote Command on {node}")
    print(f"Testing: run_remote_command('{cluster}', '{node}', 'whoami')")
    print("Expected: Execute 'whoami' and return output\n")

    result = run_remote_command(cluster, node, "whoami", user="root")
    print_result(result)

    return result


def test_list_flux(cluster, node):
    """Test 4: List Flux Kustomizations."""
    print_section(f"TEST 4: List Flux Kustomizations on {node}")
    print(f"Testing: list_flux_kustomizations('{cluster}', '{node}')")
    print("Expected: Show all Flux Kustomizations\n")

    result = list_flux_kustomizations(cluster, node)
    print_result(result)

    return result


def test_reconcile_flux(cluster, node, kustomization_name):
    """Test 5: Reconcile a Flux Kustomization."""
    print_section(f"TEST 5: Reconcile Flux Kustomization '{kustomization_name}'")
    print(
        f"Testing: reconcile_flux_kustomization('{cluster}', '{node}', '{kustomization_name}')"
    )
    print("Expected: Trigger Flux reconciliation\n")

    result = reconcile_flux_kustomization(
        cluster, node, kustomization_name, namespace="flux-system"
    )
    print_result(result)

    return result


def main():
    """Run all V1b tool tests."""
    print("\n" + "=" * 80)
    print("  PLATFORM MCP SERVER - V1b TOOLS TEST SUITE")
    print("  Teleport SSH & Remote Command Execution")
    print("=" * 80)

    # Test 1: List nodes
    nodes_results = test_list_nodes()

    # Find a node to test with
    test_cluster = None
    test_node = None

    # Try to find a node in staging first, then production
    for cluster_name in ["staging", "production"]:
        if cluster_name in nodes_results:
            result = nodes_results[cluster_name]
            if result.get("success") and result.get("nodes"):
                test_cluster = cluster_name
                test_node = result["nodes"][0]["hostname"]
                break

    if not test_cluster or not test_node:
        print_section("TESTS 2-5: Skipped")
        print("⚠️  No nodes found to test with")
        print("\nThis might mean:")
        print("  - You're not logged into any Teleport clusters")
        print("  - No SSH nodes are available in your Teleport clusters")
        print("\nTo fix:")
        print("  1. tsh login --proxy=teleport.tw.ee:443 --auth=okta staging")
        print("  2. tsh ls --cluster staging")
        print("  3. Run this test again")
    else:
        print_section("Test Target Selected")
        print(f"Cluster: {test_cluster}")
        print(f"Node: {test_node}")

        # Test 2: Verify SSH access
        access_result = test_verify_access(test_cluster, test_node)

        if access_result.get("accessible"):
            # Test 3: Run simple command
            command_result = test_run_command(test_cluster, test_node)

            # Test 4: List Flux Kustomizations
            flux_result = test_list_flux(test_cluster, test_node)

            # Test 5: Reconcile Flux (only if we found kustomizations)
            if flux_result.get("success") and flux_result.get("kustomizations"):
                kustomization_name = flux_result["kustomizations"][0]["name"]
                reconcile_result = test_reconcile_flux(
                    test_cluster, test_node, kustomization_name
                )
            else:
                print_section("TEST 5: Skipped")
                print("⚠️  No Flux Kustomizations found to test reconciliation")
        else:
            print_section("TESTS 3-5: Skipped")
            print("⚠️  Skipping remaining tests because SSH access verification failed")

    # Summary
    print_section("TEST SUMMARY")
    print("✅ Test 1: list_teleport_nodes() - Complete")

    if test_cluster and test_node:
        print("✅ Test 2: verify_ssh_access() - Complete")
        if access_result.get("accessible"):
            print("✅ Test 3: run_remote_command() - Complete")
            print("✅ Test 4: list_flux_kustomizations() - Complete")
            if flux_result.get("success") and flux_result.get("kustomizations"):
                print("✅ Test 5: reconcile_flux_kustomization() - Complete")
            else:
                print("⚠️  Test 5: reconcile_flux_kustomization() - Skipped (no Flux)")
        else:
            print("⚠️  Test 3-5: Skipped (no SSH access)")
    else:
        print("⚠️  Test 2-5: Skipped (no nodes found)")

    print("\nAll V1b tools tested!")
    print("\nNext steps:")
    print("  1. Review the output above for any issues")
    print("  2. If all looks good, commit your changes:")
    print("     cd ~/personal/git/platform-mcp-server")
    print("     git add platform_mcp.py test_teleport_v1b.py")
    print('     git commit -m "Add V1b: SSH-based remote command execution"')
    print("     git push")
    print("  3. Run Ansible to sync:")
    print("     cd ~/personal/git/ansible-mac")
    print("     ansible-playbook playbooks/platform-mcp-server.yml")
    print("  4. Restart Zed Preview to load new tools")
    print("  5. Test in Zed Preview:")
    print('     - "List nodes in staging cluster"')
    print('     - "Run kubectl get nodes on [node]"')
    print('     - "Show me Flux kustomizations"')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
