#!/usr/bin/env python3
"""
Test Efficiency Enforcement Workflow

This script tests the two-step efficiency enforcement pattern:
1. analyze_critical_path() - Analyzes tasks and returns analysis_token
2. make_roadmap_decision() - Requires the token to make decisions

Incremental testing approach:
- Step 1: Can we import and call the functions?
- Step 2: Does analyze_critical_path() return a valid token?
- Step 3: Does make_roadmap_decision() accept the token?
- Step 4: Does make_roadmap_decision() reject invalid tokens?
"""

import sys
from pathlib import Path

# Add src to path so we can import layers
sys.path.insert(0, str(Path(__file__).parent))

from src.layers import personal


def test_step_1_imports():
    """Step 1: Verify we can import and access the functions."""
    print("\n" + "="*70)
    print("STEP 1: Test Imports")
    print("="*70)
    
    try:
        assert hasattr(personal, 'analyze_critical_path'), "analyze_critical_path not found"
        assert hasattr(personal, 'make_roadmap_decision'), "make_roadmap_decision not found"
        print("✅ Both functions are importable")
        return True
    except AssertionError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_step_2_analyze_returns_token():
    """Step 2: Test that analyze_critical_path() returns a valid token."""
    print("\n" + "="*70)
    print("STEP 2: Test analyze_critical_path() Returns Token")
    print("="*70)
    
    # Create simple test tasks
    tasks = [
        {"id": "test", "name": "Test enforcement", "duration": 1, "depends_on": []},
        {"id": "phase2", "name": "Phase 2 reorganization", "duration": 3, "depends_on": ["test"]},
        {"id": "expand", "name": "Expand preconditions", "duration": 2, "depends_on": ["phase2"]}
    ]
    
    print(f"\nInput: {len(tasks)} tasks")
    for task in tasks:
        print(f"  - {task['id']}: {task['name']} (duration: {task['duration']}, depends_on: {task['depends_on']})")
    
    result = personal.analyze_critical_path(tasks, goal="expand")
    
    print(f"\nResult:")
    print(f"  success: {result.get('success')}")
    print(f"  message: {result.get('message')}")
    print(f"  analysis_token: {result.get('analysis_token', 'NOT FOUND')}")
    
    # Verify token exists and has correct format
    token = result.get('analysis_token')
    if not token:
        print("❌ No analysis_token in response")
        return False
    
    if not token.startswith('efficiency-'):
        print(f"❌ Token has wrong format: {token}")
        return False
    
    print(f"✅ Token is valid: {token[:40]}...")
    return token


def test_step_3_decision_accepts_token(token):
    """Step 3: Test that make_roadmap_decision() accepts the token."""
    print("\n" + "="*70)
    print("STEP 3: Test make_roadmap_decision() Accepts Valid Token")
    print("="*70)
    
    tasks = [
        {"id": "test", "name": "Test enforcement", "duration": 1, "depends_on": []},
        {"id": "phase2", "name": "Phase 2 reorganization", "duration": 3, "depends_on": ["test"]},
        {"id": "expand", "name": "Expand preconditions", "duration": 2, "depends_on": ["phase2"]}
    ]
    
    print(f"\nCalling make_roadmap_decision() with token: {token[:40]}...")
    
    result = personal.make_roadmap_decision(
        tasks=tasks,
        analysis_token=token,
        rationale="Testing efficiency enforcement"
    )
    
    print(f"\nResult:")
    print(f"  success: {result.get('success')}")
    print(f"  message: {result.get('message')}")
    print(f"  decision: {result.get('decision')}")
    print(f"  decision_name: {result.get('decision_name')}")
    
    if not result.get('success'):
        print(f"❌ Decision failed: {result.get('message')}")
        return False
    
    print("✅ Decision accepted valid token")
    return True


def test_step_4_decision_rejects_invalid_token():
    """Step 4: Test that make_roadmap_decision() rejects invalid tokens."""
    print("\n" + "="*70)
    print("STEP 4: Test make_roadmap_decision() Rejects Invalid Token")
    print("="*70)
    
    tasks = [
        {"id": "test", "name": "Test enforcement", "duration": 1, "depends_on": []},
        {"id": "phase2", "name": "Phase 2 reorganization", "duration": 3, "depends_on": ["test"]},
        {"id": "expand", "name": "Expand preconditions", "duration": 2, "depends_on": ["phase2"]}
    ]
    
    fake_token = "fake-token-12345"
    print(f"\nCalling make_roadmap_decision() with INVALID token: {fake_token}")
    
    result = personal.make_roadmap_decision(
        tasks=tasks,
        analysis_token=fake_token,
        rationale="Testing rejection of invalid token"
    )
    
    print(f"\nResult:")
    print(f"  success: {result.get('success')}")
    print(f"  message: {result.get('message')}")
    
    if result.get('success'):
        print(f"❌ Decision should have rejected invalid token but didn't")
        return False
    
    if "Invalid analysis token" not in result.get('message', ''):
        print(f"❌ Error message doesn't mention invalid token")
        return False
    
    print("✅ Decision correctly rejected invalid token")
    return True


def main():
    """Run all tests in sequence."""
    print("\n" + "="*70)
    print("EFFICIENCY ENFORCEMENT WORKFLOW TEST")
    print("="*70)
    print("\nTesting the two-step enforcement pattern:")
    print("1. analyze_critical_path() returns analysis_token")
    print("2. make_roadmap_decision() requires that token")
    
    # Step 1: Imports
    if not test_step_1_imports():
        print("\n❌ FAILED AT STEP 1: Cannot import functions")
        return False
    
    # Step 2: Token generation
    token = test_step_2_analyze_returns_token()
    if not token:
        print("\n❌ FAILED AT STEP 2: analyze_critical_path() didn't return token")
        return False
    
    # Step 3: Token acceptance
    if not test_step_3_decision_accepts_token(token):
        print("\n❌ FAILED AT STEP 3: make_roadmap_decision() rejected valid token")
        return False
    
    # Step 4: Token rejection
    if not test_step_4_decision_rejects_invalid_token():
        print("\n❌ FAILED AT STEP 4: make_roadmap_decision() accepted invalid token")
        return False
    
    # All tests passed
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED")
    print("="*70)
    print("\nEfficiency enforcement workflow is working correctly:")
    print("  ✅ analyze_critical_path() generates valid tokens")
    print("  ✅ make_roadmap_decision() accepts valid tokens")
    print("  ✅ make_roadmap_decision() rejects invalid tokens")
    print("\nNext steps:")
    print("  1. Commit this test to the repository")
    print("  2. Update NEXT-SESSION-START-HERE.md with results")
    print("  3. Consider what to work on next")
    print("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
