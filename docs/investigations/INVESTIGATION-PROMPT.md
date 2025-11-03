# MCP Tool Accessibility Investigation - Quick Start

**Context:** MCP server registers 27 tools, but only ~10 are accessible in Zed AI. Need to debug why.

---

## The Mystery

**What Works:**
- MCP server runs correctly (verified with `ps aux`)
- All 27 tools register successfully (confirmed via Python script)
- Some tools ARE accessible: `list_meta_workflows`, `verify_teleport_compatibility`

**What Doesn't Work:**
- Most tools NOT accessible: `analyze_critical_path`, `propose_tool_design`, `test_enforcement_workflow`
- Behavioral rules mandate using tools that can't be accessed
- This breaks the enforcement architecture

**Verification:**
```bash
cd /Users/stephen.tan/personal/git/platform-mcp-server
.venv/bin/python /tmp/list_tools_async.py
# Shows all 27 tools registered with MCP server
```

But in Zed AI:
```
analyze_critical_path() → "No tool named analyze_critical_path exists"
```

---

## Investigation Steps

### 1. Check Zed Configuration
```bash
cat ~/.config/zed/settings.json | python3 -m json.tool | grep -A 30 "context_servers"
```
**Look for:** Tool allowlists, filters, limits

### 2. Check for Tool Registration Errors
```bash
# Compare tool definitions - are they identical?
grep -B 2 "@mcp.tool()" platform_mcp.py | head -30
```

### 3. Test Direct MCP Connection
Create and run:
```python
# test_direct_mcp.py
import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def test():
    server_params = {
        "command": "/Users/stephen.tan/src/mcp-servers/platform-mcp-server/.venv/bin/python",
        "args": ["/Users/stephen.tan/src/mcp-servers/platform-mcp-server/platform_mcp.py"]
    }
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Direct MCP connection sees {len(tools)} tools:")
            for t in tools: print(f"  - {t.name}")
            
            # Try calling analyze_critical_path
            try:
                result = await session.call_tool("analyze_critical_path", 
                    {"tasks": [{"id": "test", "name": "Test", "duration": 1, "depends_on": []}]})
                print(f"\n✅ analyze_critical_path works via direct MCP: {result}")
            except Exception as e:
                print(f"\n❌ analyze_critical_path failed: {e}")

asyncio.run(test())
```

### 4. Check Zed Logs
```bash
# Common log locations:
ls -la ~/Library/Logs/Zed/ 2>/dev/null
ls -la ~/.local/share/zed/logs/ 2>/dev/null
```

### 5. Check for Tool Count Limits
```bash
# How many tools are accessible in Zed AI?
# Count by trying to list all available tools in the context
```

---

## Key Questions

1. **Is Zed filtering tools intentionally?** (Security/UX reasons)
2. **Is there an MCP protocol limit?** (Tool count or size?)
3. **Are all @mcp.tool() decorators identical?** (Registration differences?)
4. **Do accessible tools have something in common?** (Position in file? Naming pattern?)

---

## Root Cause Hypotheses

**H1: Zed has an undocumented tool limit**
- Evidence: Exactly ~10 tools accessible
- Test: Check if it's the first 10, last 10, or specific pattern

**H2: Tool registration fails silently for some tools**
- Evidence: No error messages
- Test: Check logs for registration errors

**H3: Zed filters tools by category/purpose**
- Evidence: Meta-tools work, enforcement tools don't
- Test: Look for patterns in accessible vs inaccessible tools

**H4: MCP protocol has size/complexity limits per tool**
- Evidence: Some tools have complex signatures
- Test: Try registering a simple stub tool with same name

**H5: Multiple MCP server instances running (old + new)**
- Evidence: Previous venv issue
- Test: `ps aux | grep platform_mcp` and check ALL Python paths

---

## Deliverables

Provide:
1. **Root cause** (which hypothesis is correct?)
2. **Fix** (how to make all tools accessible)
3. **Verification** (proof that `analyze_critical_path()` now works)
4. **Cleanup list** (what docs/code to remove)

---

## Success = Being Able to Run This

```python
# In Zed AI context, this should work:
result = analyze_critical_path(
    tasks=[
        {"id": "test", "name": "Test", "duration": 1, "depends_on": []}
    ]
)
print(result)  # Should return analysis with critical_path, work_order, etc.
```

---

## Files to Check

- `~/.config/zed/settings.json` - Zed MCP config
- `platform_mcp.py` - Tool definitions (line 2749+ for analyze_critical_path)
- `.rules/llm_behavioral_rules.md` - Behavioral contract (requires these tools)
- Zed logs (find location)

---

**Start here:** Run the direct MCP test script. If it shows all 27 tools and can call them, the issue is Zed-specific. If not, it's server-side.