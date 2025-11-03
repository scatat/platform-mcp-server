# Handoff to New LLM Session - Tool Accessibility Investigation

**Date:** 2025-01-07 01:10 AM  
**From:** Claude (Anthropic) via Zed  
**Status:** BLOCKED - Need investigation by fresh session  
**Priority:** HIGH - Blocks enforcement architecture  

---

## TL;DR

MCP server successfully registers 27 tools, but only ~10 are accessible to the AI in Zed. This breaks the behavioral rules enforcement system. We need to find out why and fix it.

---

## Current State

### What's Working ✅
- MCP server runs correctly with proper `.venv/bin/python` path
- All 27 tools register successfully (verified via Python script)
- Some tools ARE accessible: `list_meta_workflows`, `verify_teleport_compatibility`, `check_tsh_installed`
- Git repo is clean and pushed to `main`

### What's Broken ❌
- Most tools NOT accessible: `analyze_critical_path`, `propose_tool_design`, `test_enforcement_workflow`, `make_roadmap_decision`
- Behavioral rules mandate using these inaccessible tools
- Can't test enforcement workflows
- Can't follow Rule #3 (must use `analyze_critical_path` before roadmap decisions)

### Verification Commands
```bash
cd /Users/stephen.tan/personal/git/platform-mcp-server

# Verify server registers all tools
.venv/bin/python /tmp/list_tools_async.py
# Output: "📋 Total tools registered: 27"

# Check server processes
ps aux | grep platform_mcp | grep -v grep
# Shows 4 processes running with correct .venv path

# Try calling tool in Zed AI
# analyze_critical_path() → "No tool named analyze_critical_path exists"
```

---

## Recent Session Summary

### What We Did
1. **Fixed venv path issue** - Changed from incorrect `venv/` to correct `.venv/` (uv standard)
2. **Added behavioral rules** - `.rules/llm_behavioral_rules.md` mandates workflow enforcement
3. **Integrated Gemini's work** - Adopted behavioral enforcement approach
4. **Granted Rule #1 exception** - Allowed direct file edit to add `test_enforcement_workflow` tool
5. **Discovered tool filtering** - Realized only subset of tools accessible
6. **Created investigation docs** - Documented the mystery for next session

### What We Learned
- MCP server itself works perfectly (27 tools registered)
- Zed AI context has selective tool access (not server issue)
- This isn't a configuration problem in `~/.config/zed/settings.json` (no filtering there)
- Problem is likely in how Zed exposes MCP tools to the AI

### What We Tried
- ✅ Restarted Zed multiple times
- ✅ Fixed .venv path from `venv/` to `.venv/`
- ✅ Verified all 27 tools register with MCP server
- ✅ Checked Zed config for tool filters (none found)
- ❌ Could not make inaccessible tools accessible

---

## The Investigation Task

**Your mission:** Figure out why only some MCP tools are accessible to Zed AI and fix it.

**Key files:**
- `docs/investigations/INVESTIGATION-PROMPT.md` - Quick start guide
- `docs/investigations/TOOL-ACCESSIBILITY-DEBUG.md` - Detailed investigation steps
- `platform_mcp.py` - MCP server with 27 tools (line 2749+ for `analyze_critical_path`)
- `.rules/llm_behavioral_rules.md` - Rules that require these tools

**Start here:**
1. Read `docs/investigations/INVESTIGATION-PROMPT.md`
2. Run the direct MCP connection test
3. Check Zed logs for tool registration errors
4. Investigate hypotheses (tool limits, filtering, etc.)

---

## Hypotheses to Test

**H1: Zed has undocumented tool limit (~10 tools max)**
- Test: Count exactly how many tools are accessible
- Evidence: Consistent subset of tools work

**H2: Tool registration fails silently for some tools**
- Test: Check Zed logs for errors
- Evidence: No error messages visible

**H3: Zed filters by tool category/purpose**
- Test: Compare accessible vs inaccessible tools for patterns
- Evidence: Meta-tools work, enforcement tools don't

**H4: Multiple server instances (old code + new code)**
- Test: Check all Python paths in `ps aux` output
- Evidence: Previous venv confusion

**H5: MCP protocol has size/complexity limits**
- Test: Compare tool signatures (simple vs complex)
- Evidence: Some tools have large docstrings

---

## Success Criteria

When done, you should be able to:

```python
# In Zed AI context:
result = analyze_critical_path(
    tasks=[{"id": "test", "name": "Test", "duration": 1, "depends_on": []}]
)
# Should return: {"success": true, "critical_path": ["test"], ...}

result = test_enforcement_workflow()
# Should return: {"success": true, "message": "✅ Enforcement workflow test successful", ...}
```

---

## Important Context

### Behavioral Rules
The `.rules/llm_behavioral_rules.md` file says:
- **Rule #1:** NO direct modification of `platform_mcp.py`, `ROADMAP.md`, `design_validation.py`
- **Rule #2:** MUST use `propose_tool_design()` → `create_mcp_tool()` workflow
- **Rule #3:** MUST use `analyze_critical_path()` → `make_roadmap_decision()` workflow

**Problem:** Rules require tools that aren't accessible = enforcement is impossible

### One-Time Exception Status
Rule #1 exception was granted for testing purposes. After investigation:
- If tools become accessible: Revoke exception, reinstate rules
- If tools remain inaccessible: Need escape clause in rules for limited contexts

---

## Cleanup Tasks (After Resolution)

Once tools work, clean up:
- [ ] Remove `test_enforcement_workflow` tool (was only for testing)
- [ ] Remove investigation docs (this file and `docs/investigations/`)
- [ ] Remove `/tmp/list_tools_async.py` and `/tmp/debug_mcp.py`
- [ ] Update `.rules/llm_behavioral_rules.md` if escape clause needed
- [ ] Verify all 27 tools accessible
- [ ] Test enforcement workflows end-to-end
- [ ] Revoke Rule #1 exception

---

## Git State

**Current branch:** `main`  
**Last commit:** `9cd53b3` - "docs: Add tool accessibility investigation documents"  
**Status:** Clean working tree, all changes pushed  

**Recent commits:**
```
9cd53b3 docs: Add tool accessibility investigation documents
03c0821 test: Add test_enforcement_workflow tool
20e2935 feat: Add LLM behavioral rules for workflow enforcement
962498b feat: Implement efficiency enforcement via analysis tokens
```

---

## Questions for User (After Investigation)

1. Did you find the root cause?
2. Are all 27 tools now accessible?
3. Should we file a bug with Zed if this is a platform limitation?
4. Do the behavioral rules need an escape clause for limited contexts?

---

## Contact Information

**User:** Stephen Tan  
**Project:** Personal platform engineering automation  
**Repository:** https://github.com/scatat/platform-mcp-server  
**Related:** ansible-mac playbooks (manages MCP installation)  

---

**Good luck with the investigation! The tools exist and work - we just need to make them accessible.**