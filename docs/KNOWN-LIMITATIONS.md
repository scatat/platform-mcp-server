# Known Limitations

**Last Updated:** 2025-01-07  
**Purpose:** Document known limitations and constraints in the Platform MCP Server

---

## MCP Resources Not Supported in Zed (Yet)

**Discovered:** 2025-01-07  
**Status:** Active limitation  
**Impact:** Medium (workaround available)

### Summary

The MCP protocol specification includes **Resources** (passive data that AI can read programmatically), and our server implements them correctly using FastMCP. However, **Zed's MCP client does not yet support resource discovery or reading**.

### What We Implemented

We created 5 MCP resources with proper `@mcp.resource()` decorators:

1. `workflow://meta-workflows` - Process bank (META-WORKFLOWS.md)
2. `workflow://patterns/state-management` - State management pattern
3. `workflow://patterns/session-documentation` - Session docs template
4. `workflow://architecture/layer-model` - 3-layer architecture model
5. `workflow://rules/design-checklist` - Design rules and validation

**Server-side status:** ✅ Fully implemented and tested

### What Works

- ✅ FastMCP has complete resource support
- ✅ All 5 `@mcp.resource()` endpoints implemented
- ✅ Local testing passes (`test_resources.py`)
- ✅ Resource files exist and are valid YAML
- ✅ Code deployed to `~/src/mcp-servers/platform-mcp-server`
- ✅ MCP server runs without errors
- ✅ MCP **tools** work perfectly (e.g., `list_meta_workflows()`)

### What Doesn't Work in Zed

- ❌ Cannot access resources via `workflow://` URI scheme
- ❌ No resource listing capability from AI
- ❌ Resources not automatically loaded into AI context
- ❌ AI must use `read_file()` instead

### Root Cause

**Zed's MCP client implementation** has not yet implemented the resource discovery and reading portions of the MCP protocol specification.

This is a **client limitation**, not a server issue.

### Evidence

**Comprehensive testing performed 2025-01-07:**

1. **Server validation:** All resource endpoints work when tested locally
2. **FastMCP verification:** Confirmed FastMCP has `resource()`, `list_resources()`, `read_resource()` methods
3. **Deployment verification:** Latest code (commit 547c92f) deployed successfully
4. **Zed restart:** Full quit and restart performed
5. **AI testing:** AI cannot access `workflow://` URIs, must use filesystem

**Test report:** `.ephemeral/RESOURCE-TEST-CONTEXT.md`

### Current Workaround

**Use filesystem access instead of MCP resource protocol:**

```python
# Instead of: Access workflow://rules/design-checklist (doesn't work)
# Use: read_file("platform-mcp-server/resources/rules/design-checklist.yaml")
```

**Impact:**
- ✅ All resource content is still accessible
- ❌ Not automatic/discoverable
- ❌ Requires knowing file paths
- ❌ Less self-documenting

### Decision

**Keep resource implementation as-is** (do not convert to tools)

**Rationale:**
- Code aligns with MCP specification
- Future-proof for when Zed adds support
- Server-side implementation is correct
- Resources will work automatically once Zed supports them
- Clean architecture (resources = data, tools = actions)

### When This Will Be Fixed

**Timeline:** Unknown

**Monitoring strategy:**
- Watch Zed release notes for MCP resource support
- Test periodically with new Zed versions
- No code changes needed on our side

**When Zed adds support:**
- Resources will work immediately (no code changes)
- Update this documentation
- Remove workaround instructions from workflows

### Affected Workflows

**MW-002 (New MCP Tool Development):**
- Cannot automatically read `workflow://rules/design-checklist`
- Must use: `read_file("platform-mcp-server/resources/rules/design-checklist.yaml")`

**MW-008 (Architectural Discovery):**
- Cannot automatically reference `workflow://architecture/layer-model`
- Must use: `read_file("platform-mcp-server/resources/architecture/layer-model.yaml")`

**MW-001 (Session Summaries):**
- Cannot automatically access `workflow://patterns/session-documentation`
- Must use: `read_file("platform-mcp-server/resources/patterns/session-documentation.yaml")`

### References

- **MCP Specification:** https://modelcontextprotocol.io/docs/concepts/resources
- **FastMCP Documentation:** https://github.com/jlowin/fastmcp
- **Test Report:** `.ephemeral/RESOURCE-TEST-CONTEXT.md`
- **Implementation:** `platform_mcp.py` (lines 191, 226, 258, 292, 324)
- **Test Suite:** `test_resources.py`
- **Discovery Session:** `docs/sessions/V1-phase1/RESOURCE-VALIDATION.md` (if created)

---

## Future Limitations Section

*(Add new limitations here as discovered)*

### Template for New Limitations

**Discovered:** YYYY-MM-DD  
**Status:** Active / Resolved / Mitigated  
**Impact:** High / Medium / Low

**Summary:** Brief description of limitation

**What works / doesn't work:** Clear comparison

**Root cause:** Technical explanation

**Workaround:** How to work around it

**Decision:** What we decided to do

**Monitoring:** How we'll know when it's fixed

---

**End of Known Limitations**