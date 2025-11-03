# Tool Accessibility Investigation

**Date:** 2025-01-07  
**Issue:** MCP server registers 27 tools but only ~10 are accessible to Claude AI in Zed  
**Status:** Needs investigation by fresh LLM session  

---

## Problem Statement

The platform-mcp-server MCP server successfully registers 27 tools (verified via Python script), but when accessed through Zed's AI assistant, only a subset of tools are available. This creates a "partial enforcement" problem where behavioral rules mandate using tools that aren't accessible.

**Verified Facts:**
1. ✅ MCP server runs correctly with `.venv/bin/python`
2. ✅ All 27 tools are registered (confirmed by calling `mcp.list_tools()`)
3. ✅ Some tools ARE accessible (e.g., `list_meta_workflows`, `verify_teleport_compatibility`)
4. ❌ Most tools are NOT accessible (e.g., `analyze_critical_path`, `propose_tool_design`, `test_enforcement_workflow`)

**Tool Registration Confirmed:**
```bash
cd /Users/stephen.tan/personal/git/platform-mcp-server
.venv/bin/python /tmp/list_tools_async.py
# Output: 27 tools registered, all with @mcp.tool() decorator
```

**Accessible Tools (partial list):**
- `list_meta_workflows` ✅
- `verify_teleport_compatibility` ✅
- `check_tsh_installed` ✅
- `get_tsh_client_version` ✅
- `list_teleport_nodes` ✅

**NOT Accessible Tools:**
- `analyze_critical_path` ❌
- `propose_tool_design` ❌
- `test_enforcement_workflow` ❌
- `make_roadmap_decision` ❌
- `create_mcp_tool` ❌

---

## Investigation Tasks

### Task 1: Verify Zed MCP Configuration

**Location:** `~/.config/zed/settings.json`

**Check:**
1. Is there a tool allowlist/denylist in the configuration?
2. Are there multiple MCP server definitions for `platform-tools`?
3. Is there any filtering or limiting configuration?

**Current config:**
```json
"platform-tools": {
    "command": "/Users/stephen.tan/src/mcp-servers/platform-mcp-server/.venv/bin/python",
    "args": ["/Users/stephen.tan/src/mcp-servers/platform-mcp-server/platform_mcp.py"],
    "env": {"PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"}
}
```

### Task 2: Check MCP Server Logs

**Question:** Are there errors during tool registration that only affect some tools?

**Actions:**
1. Check if MCP server logs exist: `~/Library/Logs/Zed/` or similar
2. Look for tool registration errors
3. Check if some tools fail silently during registration

### Task 3: Investigate Tool Decorator Differences

**Hypothesis:** Maybe some tools have different decorators or registration patterns?

**Check:**
```bash
cd /Users/stephen.tan/personal/git/platform-mcp-server
grep -B 3 "def list_meta_workflows" platform_mcp.py
grep -B 3 "def analyze_critical_path" platform_mcp.py
grep -B 3 "def propose_tool_design" platform_mcp.py
```

**Question:** Are all tools using identical `@mcp.tool()` decorators?

### Task 4: Check for Tool Naming Conflicts

**Hypothesis:** Maybe Zed has built-in tools with conflicting names?

**Actions:**
1. List all available tools in the Zed AI context
2. Compare with the 27 tools from the MCP server
3. Look for naming collisions

### Task 5: Investigate FastMCP Version/Limitations

**Check:**
```bash
cd /Users/stephen.tan/personal/git/platform-mcp-server
source .venv/bin/activate
pip show fastmcp
```

**Questions:**
- Is there a tool count limit in FastMCP?
- Does the MCP protocol have a tool limit?
- Is Zed's MCP integration filtering tools?

### Task 6: Test with Direct MCP Client

**Create a minimal test script:**
```python
import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def test_mcp_tools():
    server_params = {
        "command": "/Users/stephen.tan/src/mcp-servers/platform-mcp-server/.venv/bin/python",
        "args": ["/Users/stephen.tan/src/mcp-servers/platform-mcp-server/platform_mcp.py"]
    }
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Tools available via direct MCP: {len(tools)}")
            for tool in tools:
                print(f"  - {tool.name}")

asyncio.run(test_mcp_tools())
```

**This will verify:** Do we get all 27 tools when connecting directly via MCP protocol?

---

## Context for Investigation

### Project Structure
```
platform-mcp-server/
├── platform_mcp.py          # Main MCP server (4005 lines)
├── .venv/                   # Created with `uv venv`
├── requirements.txt         # Dependencies
├── .rules/llm_behavioral_rules.md  # AI behavioral contract
└── workflow_state.py        # Workflow state tracking
```

### Recent Changes
- Fixed venv path issue (`venv/` → `.venv/`)
- Added `test_enforcement_workflow` tool under Rule #1 exception
- Restarted Zed multiple times
- Server processes are running correctly (verified with `ps aux`)

### Behavioral Rules Context
The `.rules/llm_behavioral_rules.md` file mandates that the AI MUST:
1. Use `propose_tool_design()` before creating tools
2. Use `analyze_critical_path()` before roadmap decisions
3. Never directly edit protected files

**The problem:** These rules are unenforceable if the tools aren't accessible.

---

## Expected Outcomes

After investigation, provide:

1. **Root Cause:** Why are only some tools accessible?
2. **Fix:** How to make all 27 tools accessible to Zed AI
3. **Verification:** Confirm all tools work by calling `analyze_critical_path` or `test_enforcement_workflow`
4. **Cleanup Plan:** What old/incorrect documentation needs removal

---

## Files to Review

1. `~/.config/zed/settings.json` - Zed MCP configuration
2. `/Users/stephen.tan/personal/git/platform-mcp-server/platform_mcp.py` - Tool definitions
3. Zed logs (location TBD)
4. `requirements.txt` - Dependency versions

---

## Success Criteria

✅ Understand why tool filtering occurs  
✅ All 27 MCP tools accessible to Zed AI  
✅ Can call `analyze_critical_path()` successfully  
✅ Can call `test_enforcement_workflow()` successfully  
✅ Behavioral rules are enforceable  
✅ Old/incorrect documentation identified and removed  

---

## Questions for the Investigator

1. Is this a Zed limitation or a configuration issue?
2. Are there MCP protocol limits on tool counts?
3. Is there a way to debug what Zed sees vs what the server exposes?
4. Should we file a bug with Zed if this is a platform limitation?

---

## Cleanup Tasks (After Resolution)

Once tools are working, review and remove:
- [ ] Any outdated session documentation
- [ ] Incorrect troubleshooting docs
- [ ] Test tools that are no longer needed
- [ ] Symlinks or workarounds that became obsolete
- [ ] Old venv references in documentation