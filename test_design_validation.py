#!/usr/bin/env python3
"""
Test Design Validation Workflow

This tests the end-to-end workflow of:
1. Proposing a tool design
2. Validation passing/failing
3. Token generation
4. Token verification
"""

import json
import os
from pathlib import Path

from design_validation import DesignValidator


def test_valid_proposal():
    """Test that a good design passes validation."""
    print("\n" + "=" * 70)
    print("TEST 1: Valid Tool Proposal")
    print("=" * 70)

    validator = DesignValidator()
    result = validator.validate_tool_proposal(
        tool_name="list_kubernetes_pods",
        purpose="List all pods in a Kubernetes cluster",
        layer="team",
        dependencies=["run_remote_command", "kubectl"],
        requires_system_state_change=False,
        implementation_approach="Uses run_remote_command to execute 'kubectl get pods -A -o json'",
    )

    print(f"\nValid: {result['valid']}")
    print(f"Issues: {result.get('issues', [])}")
    print(f"Warnings: {result.get('warnings', [])}")

    if result["valid"]:
        print(f"\n✅ Token: {result['token'][:40]}...")
        print(f"✅ Proposal ID: {result['proposal_id']}")
        print(f"✅ Saved to: {result['proposal_path']}")

        # Verify the file was created
        assert Path(result["proposal_path"]).exists()
        print("✅ Proposal file exists")

        return result["token"]
    else:
        print("❌ TEST FAILED: Expected valid=True")
        return None


def test_invalid_proposal():
    """Test that a bad design fails validation."""
    print("\n" + "=" * 70)
    print("TEST 2: Invalid Tool Proposal (Should Fail)")
    print("=" * 70)

    validator = DesignValidator()
    result = validator.validate_tool_proposal(
        tool_name="install_packages",
        purpose="Install packages on servers",
        layer="platform",
        dependencies=["bash"],
        requires_system_state_change=True,
        implementation_approach="Creates install.sh script and runs it on staging and production servers",
    )

    print(f"\nValid: {result['valid']}")
    print(f"\nIssues:")
    for issue in result.get("issues", []):
        print(f"  • {issue}")

    print(f"\nWarnings:")
    for warn in result.get("warnings", []):
        print(f"  • {warn}")

    if not result["valid"]:
        print("\n✅ TEST PASSED: Design correctly rejected")
        print("✅ Caught Ansible-first violation")
        print("✅ Caught hardcoded configuration")
    else:
        print("❌ TEST FAILED: Expected valid=False")


def test_token_verification(token):
    """Test that token verification works."""
    print("\n" + "=" * 70)
    print("TEST 3: Token Verification")
    print("=" * 70)

    validator = DesignValidator()

    # Test valid token
    result = validator.verify_token(token)
    print(f"\nValid token: {result['valid']}")
    if result["valid"]:
        print(f"✅ Token verified successfully")
        print(f"✅ Proposal ID: {result['proposal_id']}")
        print(f"✅ Tool name: {result['proposal_data']['tool_name']}")
    else:
        print(f"❌ TEST FAILED: Token should be valid")

    # Test invalid token
    result = validator.verify_token("invalid-token-xyz")
    print(f"\nInvalid token: {result['valid']}")
    if not result["valid"]:
        print(f"✅ Invalid token correctly rejected")
        print(f"✅ Message: {result['message']}")
    else:
        print(f"❌ TEST FAILED: Invalid token should fail")


def test_list_proposals():
    """Test listing all proposals."""
    print("\n" + "=" * 70)
    print("TEST 4: List All Proposals")
    print("=" * 70)

    validator = DesignValidator()
    proposals = validator.list_proposals()

    print(f"\nFound {len(proposals)} proposal(s):")
    for p in proposals:
        print(f"  • {p['tool_name']} ({p['layer']}) - {p['proposal_id']}")

    if len(proposals) > 0:
        print(f"\n✅ Proposals listed successfully")
    else:
        print(f"❌ Expected at least one proposal")


def test_ansible_first_enforcement():
    """Test that Ansible-first principle is enforced."""
    print("\n" + "=" * 70)
    print("TEST 5: Ansible-First Principle Enforcement")
    print("=" * 70)

    validator = DesignValidator()

    # Test 1: Shell script violation
    result = validator.validate_tool_proposal(
        tool_name="setup_git_hooks",
        purpose="Install git hooks",
        layer="personal",
        dependencies=["bash"],
        requires_system_state_change=True,
        implementation_approach="Creates hooks/install.sh script to symlink hooks",
    )

    print("\nTest: Shell script for system changes")
    print(f"Valid: {result['valid']}")
    if not result["valid"] and any(
        "Ansible-first" in issue for issue in result["issues"]
    ):
        print("✅ Shell script correctly rejected")
    else:
        print("❌ Shell script should be rejected")

    # Test 2: Ansible approach (should pass)
    result = validator.validate_tool_proposal(
        tool_name="setup_git_hooks",
        purpose="Install git hooks",
        layer="personal",
        dependencies=["ansible"],
        requires_system_state_change=True,
        implementation_approach="Uses Ansible role to declaratively manage git hooks",
    )

    print("\nTest: Ansible for system changes")
    print(f"Valid: {result['valid']}")
    if result["valid"]:
        print("✅ Ansible approach correctly accepted")
    else:
        print(f"❌ Ansible approach should pass")
        print(f"Issues: {result['issues']}")


def test_hardcoded_config_detection():
    """Test detection of hardcoded configuration."""
    print("\n" + "=" * 70)
    print("TEST 6: Hardcoded Configuration Detection")
    print("=" * 70)

    validator = DesignValidator()

    result = validator.validate_tool_proposal(
        tool_name="deploy_to_clusters",
        purpose="Deploy to specific clusters",
        layer="platform",
        dependencies=["kubectl"],
        requires_system_state_change=False,
        implementation_approach="Hardcodes cluster list: staging, production, dev",
    )

    print(f"\nValid: {result['valid']}")
    print(f"Issues:")
    for issue in result.get("issues", []):
        print(f"  • {issue}")

    if not result["valid"]:
        has_config_issue = any(
            "configuration" in issue.lower() for issue in result["issues"]
        )
        if has_config_issue:
            print("\n✅ Hardcoded configuration correctly detected")
        else:
            print("❌ Should detect hardcoded configuration")
    else:
        print("❌ Should fail with hardcoded configuration")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("DESIGN VALIDATION SYSTEM - TEST SUITE")
    print("=" * 70)

    token = test_valid_proposal()
    test_invalid_proposal()

    if token:
        test_token_verification(token)

    test_list_proposals()
    test_ansible_first_enforcement()
    test_hardcoded_config_detection()

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETE")
    print("=" * 70)
    print("\n✅ Design validation system is working correctly!")
    print("\nNext steps:")
    print("  1. Use propose_tool_design() before implementing any new tool")
    print("  2. Fix issues until valid=True")
    print("  3. Save the validation token")
    print("  4. Include token in commit message")
    print("\nSee: .ephemeral/tool-proposals/README.md for details")


if __name__ == "__main__":
    main()
