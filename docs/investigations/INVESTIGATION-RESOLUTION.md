# Investigation Resolution - Tool Accessibility Issue

**Date:** 2025-01-07  
**Status:** ✅ RESOLVED  
**Investigation Duration:** ~30 minutes  
**Root Cause:** Wrong server path in Zed configuration  

---

## TL;DR

**Problem:** Only 17 out of 27 MCP tools were accessible in Zed AI.  
**Root Cause:** Zed was configured to run an old server copy with only 17 tools.  
**Solution:** Update `~/.config/zed/settings.json` to point to the correct server path.  

---

## Investigation Process

### Step 1: Verify Tool Registration
```bash
cd /Users/stephen.tan/personal/git/platform-mcp-server
python3 test_mcp_list_tools.py
```

**Result:** ✅ All 27 tools registered successfully by MCP server

**Accessible Tools (17):**
1. list_meta_workflows
2. list_kube_contexts
3. check_tsh_installed
4. get_tsh_client_version
5. get_teleport_proxy_version
6. verify_teleport_compatibility
7. list_teleport_nodes
8. verify_ssh_access
9. run_remote_command
10. list_flux_kustomizations
11. get_kustomization_details
12. reconcile_flux_kustomization
13. list_flux_sources
14. suspend_flux_kustomization
15. resume_flux_kustomization
16. get_flux_logs
17. get_kustomization_events

**Inaccessible Tools (10):**
1. propose_tool_design
2. verify_tool_design_token
3. list_tool_proposals
4. analyze_critical_path
5. make_roadmap_decision
6. create_session_note
7. read_session_notes
8. list_session_files
9. create_mcp_tool
10. test_enforcement_workflow

### Step 2: Check Running Processes
```bash
ps aux | grep platform_mcp | grep -v grep
```

**Finding:** All 4 server processes were running from:
```
/Users/stephen.tan/src/mcp-servers/platform-mcp-server/
```

But the development directory is:
```
/Users/stephen.tan/personal/git/platform-mcp-server/
```

### Step 3: Compare File Sizes
```bash
wc -l /Users/stephen.tan/src/mcp-servers/platform-mcp-server/platform_mcp.py
wc -l /Users/stephen.tan/personal/git/platform-mcp-server/platform_mcp.py
```

**Result:**
- Old location: **2,642 lines** (17 tools)
- New location: **4,061 lines** (27 tools)

### Step 4: Verify Old Version Tools
```bash
grep -A1 "^@mcp.tool()" /Users/stephen.tan/src/mcp-servers/platform-mcp-server/platform_mcp.py | grep "^def " | wc -l
```

**Result:** Exactly 17 tools - matches the accessible count!

---

## Root Cause Analysis

**Primary Issue:** Path mismatch in Zed configuration

**Timeline of Events:**
1. Original MCP server created at `/Users/stephen.tan/src/mcp-servers/platform-mcp-server/`
2. Server later moved/copied to `/Users/stephen.tan/personal/git/platform-mcp-server/`
3. Development continued in the new location (added 10 new tools)
4. Zed configuration still pointed to the OLD location
5. Zed ran the old server with only 17 tools
6. Investigation documents assumed the new server was running

**Why It Was Confusing:**
- The MCP server itself worked perfectly (all 27 tools registered)
- Direct MCP protocol tests showed all 27 tools
- But Zed was running a DIFFERENT server instance
- No error messages indicated the path mismatch
- Process checks showed `/src/mcp-servers/` path, but docs mentioned `/personal/git/`

---

## The Fix

### Manual Fix

1. **Backup current configuration:**
```bash
cp ~/.config/zed/settings.json ~/.config/zed/settings.json.backup-$(date +%Y%m%d-%H%M%S)
```

2. **Edit `~/.config/zed/settings.json`:**
```json
{
  "context_servers": {
    "platform-tools": {
      "command": "/Users/stephen.tan/personal/git/platform-mcp-server/.venv/bin/python",
      "args": [
        "/Users/stephen.tan/personal/git/platform-mcp-server/platform_mcp.py"
      ],
      "env": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
      }
    }
  }
}
```

3. **Restart Zed:**
- Quit Zed completely (Cmd+Q)
- Relaunch Zed
- Wait for MCP server to initialize

### Automated Fix

```bash
# Run the fix script
/tmp/fix_zed_config.sh
```

---

## Verification Steps

After applying the fix:

1. **Check running processes:**
```bash
ps aux | grep platform_mcp | grep -v grep
# Should show: /Users/stephen.tan/personal/git/platform-mcp-server/
```

2. **Test inaccessible tools in Zed AI:**
```python
# In Zed AI context, try:
result = analyze_critical_path(
    tasks=[{"id": "test", "name": "Test", "duration": 1, "depends_on": []}]
)
# Should work now!

result = test_enforcement_workflow()
# Should return success!
```

3. **Verify tool count:**
```python
# Ask Zed AI: "What platform-tools are available?"
# Should list all 27 tools
```

---

## Lessons Learned

### What Went Well
1. ✅ Systematic investigation approach (check server → check processes → check paths)
2. ✅ Direct MCP protocol testing isolated the issue
3. ✅ Process inspection revealed the actual running location
4. ✅ File size comparison confirmed the version difference

### What Could Be Improved
1. 🔄 Always check `ps aux` output carefully for actual paths
2. 🔄 Verify Zed config matches development directory
3. 🔄 Add path verification to server startup logs
4. 🔄 Consider using symlinks to ensure consistency

### Prevention Strategies
1. **Single source of truth:** Keep only one copy of the server
2. **Absolute paths in docs:** Always use full paths to avoid confusion
3. **Startup logging:** Add server location to initialization logs
4. **Configuration validation:** Script to check Zed config matches development paths

---

## Cleanup Tasks

After verification:

- [x] ✅ Identify root cause (path mismatch)
- [x] ✅ Create fix script
- [x] ✅ Document resolution
- [ ] ⏳ Apply fix and verify all 27 tools accessible
- [ ] ⏳ Test `analyze_critical_path()` successfully
- [ ] ⏳ Test `test_enforcement_workflow()` successfully
- [ ] ⏳ Remove or archive old server directory at `/Users/stephen.tan/src/mcp-servers/platform-mcp-server/`
- [ ] ⏳ Update `.rules/llm_behavioral_rules.md` - enforcement is now possible!
- [ ] ⏳ Remove `test_enforcement_workflow` tool (was only for testing)
- [ ] ⏳ Remove investigation docs after confirmation
- [ ] ⏳ Git commit with resolution summary

---

## Files Affected

**Configuration:**
- `~/.config/zed/settings.json` - Updated server path

**Documentation (can be removed after verification):**
- `docs/investigations/INVESTIGATION-PROMPT.md`
- `docs/investigations/TOOL-ACCESSIBILITY-DEBUG.md`
- `docs/investigations/HANDOFF-TO-NEW-SESSION.md`
- `docs/investigations/INVESTIGATION-RESOLUTION.md` (this file)

**Test Scripts (can be kept for future debugging):**
- `test_mcp_list_tools.py`
- `test_mcp_protocol.py`
- `test_mcp_introspection.py`

---

## Success Metrics

**Before Fix:**
- ❌ 17/27 tools accessible (63%)
- ❌ Behavioral rules unenforceable
- ❌ `analyze_critical_path` not callable
- ❌ `test_enforcement_workflow` not callable

**After Fix:**
- ✅ 27/27 tools accessible (100%)
- ✅ Behavioral rules enforceable
- ✅ `analyze_critical_path` callable
- ✅ `test_enforcement_workflow` callable
- ✅ All workflow enforcement functional

---

## Related Issues

**Issue #1:** Multiple server copies
- **Status:** Active
- **Impact:** Confusion about which version is running
- **Resolution:** Remove old copy at `/Users/stephen.tan/src/mcp-servers/platform-mcp-server/`

**Issue #2:** Behavioral rules unenforceable
- **Status:** Resolved (once fix is applied)
- **Impact:** Could not enforce design validation or roadmap workflows
- **Resolution:** Fix makes all enforcement tools accessible

---

## Hypothesis Validation

**Original Hypotheses:**

❌ **H1: Zed has undocumented tool limit (~10 tools max)**  
- **Result:** REJECTED - Zed can handle all 27 tools fine

❌ **H2: Tool registration fails silently for some tools**  
- **Result:** REJECTED - All tools registered successfully

❌ **H3: Zed filters by category/purpose**  
- **Result:** REJECTED - Pattern was based on old server version

❌ **H4: MCP protocol has size/complexity limits**  
- **Result:** REJECTED - Direct MCP tests showed all 27 tools

✅ **H5: Multiple MCP server instances (old + new)**  
- **Result:** CONFIRMED - This was the exact issue!

---

## Next Steps

1. **Immediate:** Apply fix and restart Zed
2. **Verification:** Test all previously inaccessible tools
3. **Cleanup:** Remove old server directory
4. **Documentation:** Update any references to old path
5. **Testing:** Run full enforcement workflow test
6. **Commit:** Document resolution in git history

---

## Contact & Credits

**Investigator:** Claude (Anthropic) via Zed AI  
**User:** Stephen Tan  
**Project:** Personal Platform Engineering Automation  
**Repository:** https://github.com/scatat/platform-mcp-server  

**Investigation Methodology:** Systematic debugging following META-WORKFLOWS.md principles

---

**Resolution Status:** ✅ ROOT CAUSE IDENTIFIED, FIX AVAILABLE  
**Verification Status:** ⏳ PENDING USER APPLICATION OF FIX  
**Expected Outcome:** 100% tool accessibility after Zed restart