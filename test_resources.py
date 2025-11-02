#!/usr/bin/env python3
"""
Test script for MCP Resources.

This validates that all resource endpoints are properly wired up and can
read their respective YAML files.

Run this before deploying to Zed to ensure resources work locally.
"""

import os
import sys


def test_resource_files_exist():
    """Test that all YAML resource files exist."""
    print("=" * 80)
    print("TEST 1: Resource Files Exist")
    print("=" * 80)

    resources = [
        "META-WORKFLOWS.md",
        "resources/patterns/state-management.yaml",
        "resources/patterns/session-documentation.yaml",
        "resources/architecture/layer-model.yaml",
        "resources/rules/design-checklist.yaml",
    ]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    all_exist = True

    for resource in resources:
        path = os.path.join(script_dir, resource)
        exists = os.path.exists(path)
        status = "✅" if exists else "❌"
        print(f"{status} {resource}")
        if not exists:
            all_exist = False
            print(f"   Missing: {path}")

    print()
    return all_exist


def test_resource_endpoints():
    """Test that all resource endpoint functions work."""
    print("=" * 80)
    print("TEST 2: Resource Endpoints Work")
    print("=" * 80)

    # Import the server
    try:
        from platform_mcp import (
            get_design_checklist_resource,
            get_layer_model_resource,
            get_meta_workflows_resource,
            get_session_documentation_pattern,
            get_state_management_pattern,
        )
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return False

    endpoints = [
        ("workflow://meta-workflows", get_meta_workflows_resource),
        ("workflow://patterns/state-management", get_state_management_pattern),
        (
            "workflow://patterns/session-documentation",
            get_session_documentation_pattern,
        ),
        ("workflow://architecture/layer-model", get_layer_model_resource),
        ("workflow://rules/design-checklist", get_design_checklist_resource),
    ]

    all_pass = True

    for uri, func in endpoints:
        try:
            content = func()

            # Check for error messages
            if content.startswith("❌"):
                print(f"❌ {uri}")
                print(f"   Error: {content}")
                all_pass = False
            else:
                # Verify content is not empty
                if len(content) > 0:
                    # Show first few chars to confirm it loaded
                    preview = content[:60].replace("\n", "\\n")
                    print(f"✅ {uri}")
                    print(f"   Preview: {preview}...")
                    print(f"   Length: {len(content)} bytes")
                else:
                    print(f"❌ {uri}")
                    print(f"   Error: Content is empty")
                    all_pass = False

        except Exception as e:
            print(f"❌ {uri}")
            print(f"   Exception: {e}")
            all_pass = False

    print()
    return all_pass


def test_yaml_parseable():
    """Test that YAML files are valid."""
    print("=" * 80)
    print("TEST 3: YAML Files Are Valid")
    print("=" * 80)

    try:
        import yaml
    except ImportError:
        print("⚠️  PyYAML not installed, skipping YAML validation")
        print()
        return True

    yaml_files = [
        "resources/patterns/state-management.yaml",
        "resources/patterns/session-documentation.yaml",
        "resources/architecture/layer-model.yaml",
        "resources/rules/design-checklist.yaml",
    ]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    all_valid = True

    for yaml_file in yaml_files:
        path = os.path.join(script_dir, yaml_file)
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)

            if data is None:
                print(f"⚠️  {yaml_file} - Empty YAML")
            else:
                print(f"✅ {yaml_file}")
                # Show top-level keys
                if isinstance(data, dict):
                    keys = list(data.keys())[:5]
                    print(f"   Keys: {', '.join(keys)}")

        except FileNotFoundError:
            print(f"❌ {yaml_file} - File not found")
            all_valid = False
        except yaml.YAMLError as e:
            print(f"❌ {yaml_file} - Invalid YAML")
            print(f"   Error: {e}")
            all_valid = False
        except Exception as e:
            print(f"❌ {yaml_file} - Error: {e}")
            all_valid = False

    print()
    return all_valid


def main():
    """Run all tests."""
    print()
    print("🧪 Testing MCP Resources")
    print()

    results = []

    # Test 1: Files exist
    results.append(("Resource files exist", test_resource_files_exist()))

    # Test 2: Endpoints work
    results.append(("Resource endpoints work", test_resource_endpoints()))

    # Test 3: YAML is valid
    results.append(("YAML files are valid", test_yaml_parseable()))

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print()

    if all_passed:
        print("🎉 All tests passed! Resources are ready to deploy.")
        print()
        print("Next steps:")
        print("1. git add platform_mcp.py test_resources.py")
        print("2. git commit -m 'Add design-checklist resource endpoint'")
        print("3. git push")
        print("4. cd ~/personal/git/ansible-mac")
        print("5. ansible-playbook playbooks/zed-mcp.yml")
        print("6. Restart Zed Preview")
        print("7. Test resource discovery in Zed")
        return 0
    else:
        print("❌ Some tests failed. Fix issues before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
