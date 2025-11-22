# Bug Fix: MCP Decorator Order Issue

**Date:** November 3, 2024
**Status:** ✅ Fixed
**Commit:** 1c8b9f5
**Severity:** Critical (Server couldn't start)

---

## Problem Statement

The platform-mcp-server failed to start with a `NameError`:

```python
NameError: name 'mcp' is not defined. Did you mean: 'map'?
```

**Location:** `src/layers/personal.py`, line 582

The server appeared to be configured correctly in Zed, but would timeout when attempting to start, causing it to disappear from the context servers list.

---

## Investigation Process

### Step 1: Manual Server Test

```bash
cd ~/personal/git/platform-mcp-server
.venv/bin/python platform_mcp.py
```

**Result:** Immediate `NameError` on import.

### Step 2: Root Cause Analysis

The bug was in the **import order**:

**In `src/layers/personal.py` (line 582):**
```python
@mcp.resource("workflow://meta-workflows")
def get_meta_workflows_resource() -> str:
    # ...
```

**In `platform_mcp.py`:**
```python
# Line 35: Import personal module (runs all module-level code)
from src.layers import personal, platform

# Line 69: Create mcp object (TOO LATE!)
mcp = FastMCP("platform-tools")
```

**The Problem:** When Python imports `personal.py`, it executes the module-level decorators (`@mcp.resource`) **before** the `mcp` object exists in `platform_mcp.py`.

### Step 3: Historical Analysis

Checked if this ever worked:

```bash
git checkout a3c229d  # "Phase 2 Complete: Implement 3-layer architecture"
.venv/bin/python platform_mcp.py
# Result: Same NameError!
```

**Finding:** This bug existed since the 3-layer architecture was introduced on Nov 3, 2025. It **never worked**.

### Step 4: Why Did It Seem to Work Before?

The server likely appeared to work because:
1. **Different location was running**: The old `~/src/mcp-servers/platform-mcp-server` clone (before cleanup)
2. **Resources weren't being used**: The tools worked, but resource endpoints silently failed
3. **Silent failures**: Zed showed timeout errors but didn't clearly indicate the cause

---

## The Fix

### Changes Made

#### 1. Removed Decorators from `personal.py`

**Before:**
```python
@mcp.resource("workflow://meta-workflows")
def get_meta_workflows_resource() -> str:
    # ...

@mcp.prompt()
def new_tool_workflow() -> str:
    # ...
```

**After:**
```python
# Plain functions without decorators
def get_meta_workflows_resource() -> str:
    # ...

def new_tool_workflow() -> str:
    # ...
```

#### 2. Register After MCP Creation in `platform_mcp.py`

**Added before `if __name__ == "__main__"`:**
```python
# =============================================================================
# RESOURCES REGISTRATION
# =============================================================================
# Register MCP resources (documentation, patterns, etc.)
# These must be registered after mcp is created

mcp.resource("workflow://meta-workflows")(personal.get_meta_workflows_resource)
mcp.resource("workflow://patterns/state-management")(
    personal.get_state_management_pattern
)
mcp.resource("workflow://patterns/session-documentation")(
    personal.get_session_documentation_pattern
)
mcp.resource("workflow://architecture/layer-model")(personal.get_layer_model_resource)
mcp.resource("workflow://rules/design-checklist")(
    personal.get_design_checklist_resource
)

# =============================================================================
# PROMPTS REGISTRATION
# =============================================================================
# Register MCP prompts (workflow shortcuts)
# These must be registered after mcp is created

mcp.prompt()(personal.new_tool_workflow)
mcp.prompt()(personal.end_session_workflow)
mcp.prompt()(personal.debug_flux_workflow)
mcp.prompt()(personal.validate_design_workflow)
```

#### 3. Removed Duplicate Definitions

The `platform_mcp.py` file had duplicate resource and prompt definitions with decorators (lines 295-380). These were removed since we're now using the functions from `personal.py`.

---

## Verification

### Test 1: Module Import
```bash
.venv/bin/python -c "import platform_mcp; print('✓ OK')"
# Output: ✓ OK
```

### Test 2: Server Start (Manual)
```bash
.venv/bin/python platform_mcp.py
# Server starts and waits for input (expected behavior)
```

### Test 3: Zed Integration
1. Restart Zed
2. Check context servers list
3. Verify platform-tools appears
4. Test a tool invocation

---

## Root Cause: Python Decorator Execution Time

### The Core Issue

Python decorators are **syntactic sugar** that execute at **module import time**:

```python
@decorator
def function():
    pass

# Is equivalent to:
def function():
    pass
function = decorator(function)  # Runs immediately when module loads!
```

When you write:
```python
@mcp.resource("...")
def my_function():
    pass
```

Python executes `mcp.resource("...")` **immediately** when the module is imported, not when the function is called.

### The Import Chain

1. `platform_mcp.py` imports `personal.py`
2. Python loads `personal.py` and executes all module-level code
3. Decorators like `@mcp.resource(...)` try to execute
4. `mcp` doesn't exist yet → `NameError`
5. Import fails before `mcp = FastMCP(...)` line is reached

### The Solution

**Option 1 (Chosen):** Register after creation
```python
# In main file, after mcp is created:
mcp.resource("uri")(personal.function_name)
```

**Option 2:** Lazy evaluation (not used)
```python
# Would require changing the decorator implementation
def register_resources(mcp_instance):
    # Register all resources here
    pass
```

---

## Lessons Learned

### 1. Decorator Timing Matters

Decorators that depend on global objects must ensure those objects exist **before** the module containing the decorators is imported.

### 2. Test Immediately After Major Refactors

The 3-layer architecture refactor (commit a3c229d) introduced this bug but wasn't tested immediately. The bug sat dormant until the duplicate server location was cleaned up.

### 3. Import Order is Critical

When reorganizing code into modules, always verify:
1. What runs at import time?
2. What order do modules import?
3. Are all dependencies available when needed?

### 4. MCP Server Testing

MCP servers need special testing because:
- They wait for stdin (don't exit immediately)
- Errors during import can be silent in Zed
- Timeouts don't always show the underlying error

**Better test:**
```bash
python -c "import your_server" && echo "OK"
```

---

## Prevention

### Future Architecture Pattern

For MCP servers with layered architecture:

```python
# layer_module.py
# Define plain functions (no decorators that depend on external objects)

def my_resource():
    return "content"

# main.py
from layer_module import my_resource

# Create MCP instance
mcp = FastMCP("name")

# Register after creation
mcp.resource("uri")(my_resource)

# Or use a registration function
def register_layer_resources(mcp_instance):
    mcp_instance.resource("uri")(my_resource)
    # ... more registrations

register_layer_resources(mcp)
```

### Testing Checklist

Before committing MCP server changes:

- [ ] Module imports without errors: `python -c "import server_module"`
- [ ] Server starts manually: `python server.py` (test a few seconds)
- [ ] No import-time decorator dependencies
- [ ] Test in Zed with server restart
- [ ] Check Zed logs for errors: `tail -f ~/Library/Logs/Zed/Zed.log`

---

## Related Issues

- [Platform MCP Cleanup](PLATFORM_MCP_CLEANUP.md) - Canonical location fix
- [WhatsApp MCP Removal](../ansible-mac/docs/MCP_WHATSAPP_REMOVAL_JIRA_ADDITION.md)

---

## Timeline

| Time | Event |
|------|-------|
| Nov 3, 01:36 | Bug introduced in commit a3c229d (3-layer architecture) |
| Nov 3, 17:00 | Bug discovered during Zed configuration update |
| Nov 3, 17:05 | Investigation: Systematic debugging, no assumptions |
| Nov 3, 17:10 | Root cause identified: Decorator execution order |
| Nov 3, 17:12 | Historical analysis: Never worked since introduction |
| Nov 3, 17:14 | Fix implemented and tested |
| Nov 3, 17:15 | Committed as 1c8b9f5 |

**Total Debug Time:** ~15 minutes (systematic approach paid off!)

---

## Commit Message

```
fix: Register resources and prompts after mcp object creation

The @mcp.resource and @mcp.prompt decorators were being used at module
import time in personal.py, before the mcp object was created in
platform_mcp.py. This caused a NameError.

Changes:
- Removed decorators from personal.py functions
- Register resources and prompts in platform_mcp.py after mcp is created
- Removed duplicate resource/prompt definitions from platform_mcp.py

This bug existed since commit a3c229d (Phase 2) and prevented the
server from starting.

Fixes: NameError: name 'mcp' is not defined
```

---

**Status:** ✅ Fixed and verified
**Next Steps:** Restart Zed and verify platform-tools MCP server appears in context servers list