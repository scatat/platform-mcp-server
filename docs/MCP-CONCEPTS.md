# MCP Concepts - Tools vs Resources

**A beginner-friendly guide to understanding the Model Context Protocol (MCP) architecture**

---

## What is MCP?

The **Model Context Protocol (MCP)** is a standard for connecting AI assistants to external tools and data sources.

**Analogy**: Think of MCP like a **REST API for AI agents**.
- Your AI assistant is the **client**
- This platform-mcp-server is the **server**
- Tools and Resources are the **endpoints**

---

## Two Core Concepts

### 1. **Tools** (Functions AI Can Execute)

**What they are**: Actions the AI can perform

**Analogy**: Like clicking a button in a web UI
- Each tool is a function the AI can call
- Tools can modify state, run commands, or fetch data
- Tools return results to the AI

**Examples from this server**:
```python
# List available Kubernetes contexts
list_kube_contexts()

# Suspend a Flux kustomization
suspend_flux_kustomization(cluster="staging", node="k8s-01", name="apps")

# Execute remote command via Teleport
run_remote_command(cluster="production", node="bastion", command="uptime")
```

**When to create a tool**:
- ✅ When AI needs to **DO** something (execute, modify, create)
- ✅ When the operation has **side effects** (changes state)
- ✅ When you need **parameters** (inputs from AI)
- ✅ When the result depends on **current system state**

**Tool characteristics**:
- **Imperative**: "Do this action"
- **Stateful**: Results depend on current system state
- **Parameters**: Accept inputs from AI
- **Side effects**: May change the system
- **Dynamic results**: Output varies based on execution time

---

### 2. **Resources** (Data AI Can Read)

**What they are**: Static or semi-static data the AI can reference

**Analogy**: Like reading a configuration file or documentation
- Resources are read-only data sources
- AI can access them for context or reference
- Resources don't execute code, they just return data

**Examples from this server**:
```
workflow://meta-workflows
  ↳ Returns: Full content of META-WORKFLOWS.md

workflow://patterns/state-management
  ↳ Returns: State management pattern YAML

workflow://architecture/layer-model
  ↳ Returns: 3-layer architecture definition
```

**When to create a resource**:
- ✅ When AI needs to **READ** reference data (docs, configs, patterns)
- ✅ When data is **relatively static** (changes infrequently)
- ✅ When you want AI to **understand** system architecture/patterns
- ✅ When data is **structured** (YAML, JSON, Markdown)
- ✅ When building a **self-describing system**

**Resource characteristics**:
- **Declarative**: "Here's the data"
- **Stateless**: Same data every time (until updated)
- **No parameters**: Just return the data
- **No side effects**: Read-only
- **Static or semi-static**: Content doesn't change frequently

---

## Comparison Table

| Aspect | Tools | Resources |
|--------|-------|-----------|
| **Purpose** | Execute actions | Provide reference data |
| **Analogy** | REST POST/PUT/DELETE | REST GET |
| **Example** | `suspend_flux_kustomization()` | `workflow://patterns/state-management` |
| **Parameters** | ✅ Yes (cluster, node, name) | ❌ No (just return data) |
| **Side Effects** | ✅ Yes (may change system) | ❌ No (read-only) |
| **State** | Dynamic (depends on runtime) | Static/semi-static |
| **When to use** | "Do this" | "Show me how" |
| **Code** | Python functions with logic | File read + return content |
| **Frequency** | Called when action needed | Referenced for context |

---

## Real-World Examples

### Scenario 1: Debugging Flux

**AI needs to**:
1. Understand how Flux debugging works → **Resource**
2. List current kustomizations → **Tool**
3. Get events for a specific kustomization → **Tool**
4. Suspend a failing kustomization → **Tool**

**Flow**:
```
AI: "Debug Flux issues on staging cluster"

1. Read resource: workflow://meta-workflows
   → Finds MW-006 (Flux Debugging Session)
   → Understands the process

2. Call tool: list_flux_kustomizations(cluster="staging", node="k8s-01")
   → Returns: 12 kustomizations, 1 failing

3. Call tool: get_kustomization_events(name="apps.backend")
   → Returns: "ImagePullBackOff" error

4. Call tool: suspend_flux_kustomization(name="apps.backend")
   → Suspends reconciliation to prevent noise
```

**Why this mix?**
- **Resource** (MW-006) provides the **workflow/process**
- **Tools** perform the **actual operations**

---

### Scenario 2: Creating Session Summary

**AI needs to**:
1. Understand session documentation pattern → **Resource**
2. Review current session notes → **File read (not MCP)**
3. Create final summary → **File write (not MCP)**

**Flow**:
```
AI: "This thread is ending" (triggers MW-001)

1. Read resource: workflow://patterns/session-documentation
   → Gets template structure
   → Understands extraction rules

2. Read ephemeral notes: .ephemeral/sessions/current-work.md
   → Gets raw session data

3. Extract information and create: docs/sessions/V1d/FINAL-SUMMARY.md
   → Applies template from resource
```

**Why this mix?**
- **Resource** provides the **template and rules**
- **File operations** handle the **actual work**

---

## How They Work Together

### Pattern: Self-Describing System

**Goal**: AI should be able to discover and understand the system without hardcoded knowledge

**Architecture**:
```
Resources (What/How)     →     Tools (Do)
     ↓                              ↓
  Patterns                      Execution
  Templates                     Operations
  Workflows                     Commands
  Architecture                  State changes
```

**Example Flow**:
```
1. AI reads resource: workflow://meta-workflows
   → Discovers MW-002 (New MCP Tool Development)

2. AI reads resource: workflow://patterns/state-management
   → Understands where to put files

3. AI calls tool: list_meta_workflows()
   → Gets current workflow count (validates understanding)

4. AI creates new tool following the pattern from resources
```

**Benefits**:
- ✅ **Discoverable**: AI can learn about system at runtime
- ✅ **Consistent**: Resources define patterns, tools follow them
- ✅ **Evolvable**: Update resources to change AI behavior
- ✅ **Self-documenting**: Resources are both docs and configuration

---

## Implementation in This Server

### Tool Registration (Python)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("platform-tools")

@mcp.tool()
def suspend_flux_kustomization(cluster: str, node: str, name: str) -> Dict[str, Any]:
    """
    Suspend a Flux Kustomization (pause reconciliation).
    
    Args:
        cluster: Teleport cluster name
        node: Kubernetes node hostname
        name: Kustomization name
    
    Returns:
        dict: Suspension results
    """
    # Implementation here
    return {"success": True, "message": "Suspended"}
```

**Key parts**:
- `@mcp.tool()` - Registers function as MCP tool
- Docstring - AI reads this to understand what tool does
- Type hints - Define parameter types
- Return value - Results sent back to AI

---

### Resource Registration (Python)

```python
@mcp.resource("workflow://patterns/state-management")
def get_state_management_pattern() -> str:
    """
    MCP Resource: State Management Pattern (transient vs persistent state).
    
    Returns:
        str: Full content of resources/patterns/state-management.yaml
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pattern_path = os.path.join(script_dir, "resources/patterns/state-management.yaml")
    
    with open(pattern_path, "r") as f:
        return f.read()
```

**Key parts**:
- `@mcp.resource("workflow://...")` - Registers resource with URI
- URI scheme - `workflow://` is our custom scheme
- Return type - Always returns string (file content)
- Read-only - Just reads and returns, no side effects

---

## URI Schemes for Resources

This server uses custom URI schemes to organize resources:

```
workflow://meta-workflows
  ↳ META-WORKFLOWS.md content

workflow://patterns/state-management
  ↳ State management pattern YAML

workflow://patterns/session-documentation
  ↳ Session documentation pattern YAML

workflow://architecture/layer-model
  ↳ 3-layer architecture model YAML
```

**Why custom schemes?**
- Namespacing (organize by category)
- Self-describing (URI tells you what it contains)
- Future-proof (can add new schemes as needed)

---

## Best Practices

### When Creating a Tool

**DO**:
- ✅ Write detailed docstrings (AI reads these!)
- ✅ Use type hints for parameters
- ✅ Return structured data (dicts, not just strings)
- ✅ Include error handling and guidance
- ✅ Use `shlex.quote()` for user inputs (security!)
- ✅ Provide `ansible_command` and `ansible_steps` on errors

**DON'T**:
- ❌ Use `shell=True` in subprocess calls (security risk!)
- ❌ Return only error messages (provide guidance!)
- ❌ Assume AI knows your infrastructure (be explicit!)
- ❌ Skip validation (check inputs first!)

**Example of good error handling**:
```python
return {
    "success": False,
    "message": "❌ Not logged into staging cluster",
    "ansible_steps": [
        "tsh login --proxy=teleport.example.com --auth=okta staging",
        "Verify: tsh status"
    ]
}
```

---

### When Creating a Resource

**DO**:
- ✅ Use structured formats (YAML, JSON, Markdown)
- ✅ Include metadata (version, created date, author)
- ✅ Document the schema/structure
- ✅ Keep it focused (one pattern/concept per resource)
- ✅ Make it self-describing

**DON'T**:
- ❌ Mix concerns (one resource = one pattern)
- ❌ Use proprietary formats (stick to standards)
- ❌ Duplicate data (reference other resources instead)
- ❌ Include secrets or sensitive data

**Example resource structure**:
```yaml
# Good structure
pattern:
  name: "State Management"
  id: "state-mgmt-001"
  version: "1.0.0"
  
directories:
  transient:
    path: ".ephemeral/"
    purpose: "..."
    
rules:
  store_in_ephemeral:
    - "Session notes"
    - "Test outputs"
```

---

## How AI Uses This

### Discovery Phase

```
1. AI connects to MCP server
2. Server advertises available tools and resources
3. AI can list all tools: list_tools()
4. AI can list all resources: list_resources()
5. AI reads resources to understand patterns
6. AI calls tools to perform operations
```

### Execution Phase

```
User: "Debug Flux on staging"

AI Internal Process:
1. Check if workflow exists: Read workflow://meta-workflows
2. Find MW-006 (Flux Debugging)
3. Follow workflow steps
4. Call tools as needed: list_flux_kustomizations(), get_events(), etc.
5. Report results to user
```

---

## Common Patterns

### Pattern 1: Workflow + Tools

**Resource defines the workflow**:
```yaml
# workflow://meta-workflows (excerpt)
MW-006:
  name: "Flux Debugging"
  steps:
    - "List kustomizations"
    - "Check events"
    - "Suspend if needed"
```

**Tools execute the steps**:
```python
list_flux_kustomizations()
get_kustomization_events()
suspend_flux_kustomization()
```

---

### Pattern 2: Template + File Creation

**Resource provides template**:
```yaml
# workflow://patterns/session-documentation
template:
  sections:
    - "🎯 What We Accomplished"
    - "🔑 Key Decisions"
    - "🧪 Testing Results"
```

**AI applies template**:
```python
# AI reads resource
template = read_resource("workflow://patterns/session-documentation")

# AI creates file following template
create_file("docs/sessions/V1d/FINAL-SUMMARY.md", using=template)
```

---

## Debugging Tips

### Tools Not Working?

```bash
# Check if MCP server is running
ps aux | grep platform_mcp

# Test tool directly
python3 -c "from platform_mcp import list_meta_workflows; print(list_meta_workflows())"

# Check MCP server logs
# (Depends on how you're running it - Zed, Claude Desktop, etc.)
```

### Resources Not Available?

```bash
# Check if resource file exists
ls -la resources/patterns/state-management.yaml

# Test resource endpoint
python3 -c "from platform_mcp import get_state_management_pattern; print(get_state_management_pattern())"

# Verify resource registration in platform_mcp.py
grep "@mcp.resource" platform_mcp.py
```

---

## Further Reading

- **MCP Specification**: https://modelcontextprotocol.io/
- **FastMCP Documentation**: https://github.com/jlowin/fastmcp
- **This Server's Design**: `docs/DESIGN-PRINCIPLES.md`
- **Architecture Model**: `resources/architecture/layer-model.yaml`
- **Meta-Workflows**: `META-WORKFLOWS.md`

---

## Quick Reference

| I want to... | Create a... | Example |
|-------------|-------------|---------|
| Execute commands | **Tool** | `run_remote_command()` |
| Read configuration | **Resource** | `workflow://patterns/X` |
| Modify system state | **Tool** | `suspend_flux_kustomization()` |
| Provide templates | **Resource** | `workflow://patterns/session-documentation` |
| Document workflows | **Resource** | `workflow://meta-workflows` |
| Fetch dynamic data | **Tool** | `list_flux_kustomizations()` |
| Define patterns | **Resource** | `workflow://architecture/layer-model` |

---

## Summary

**Tools** = Do things (imperative, stateful, dynamic)
**Resources** = Know things (declarative, stateless, static)

Together, they make a **self-describing, discoverable, evolvable system** that AI can understand and operate without hardcoded knowledge.

**The key insight**: Separate **what/how** (resources) from **do** (tools). This enables AI to learn patterns at runtime and adapt to changes without code modifications.