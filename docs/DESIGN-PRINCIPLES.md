# Design Principles for Evolution & Decoupling

**Purpose:** Guard against unknown future constraints by designing for change  
**Audience:** AI agents, developers extending this MCP server, teams forking this code  
**Status:** Living Document  
**Created:** 2024-01-07

> **Note:** This document provides comprehensive explanations and context.  
> For structured, actionable rules that the AI can check programmatically,  
> see **`resources/rules/design-checklist.yaml`** (MCP Resource).

---

## The Core Challenge

> "We're making this up as we go along. I fear constraints I wasn't aware of will appear."

**The Problem:**
- Requirements discovered incrementally
- Infrastructure assumptions may be wrong
- Teams have different patterns
- Future needs are unknown

**The Goal:**
Design an architecture that can **evolve without breaking**.

---

## Foundational Principles

### 1. Separation of Concerns

**Principle:** Different responsibilities belong in different places.

**In Practice:**
- **Layers** separate organizational boundaries (Platform/Team/Personal)
- **Tools** separate capabilities (authentication, execution, management)
- **Workflows** separate processes (how to accomplish tasks)
- **State** separates persistence (git vs ephemeral)

**Why It Matters:**
Changes in one area don't cascade into others.

**Example:**
```
Team changes K8s access from SSH → kube API
├─ Platform layer: Unchanged ✓
├─ Team layer: Modified ✓
└─ Personal layer: Unchanged ✓
```

---

### 2. Loose Coupling via Interfaces

**Principle:** Depend on contracts (what), not implementations (how).

**Bad (Tight Coupling):**
```python
# Team tool directly depends on platform implementation
def list_flux_kustomizations(cluster, node):
    # Hardcoded to use run_remote_command
    result = run_remote_command(cluster, node, "kubectl get kustomizations")
    return parse_json(result)
```

**Good (Loose Coupling):**
```python
# Team tool depends on interface
def list_flux_kustomizations(cluster, executor):
    # executor could be SSH, kube API, or anything implementing the interface
    result = executor.execute("kubectl get kustomizations")
    return parse_json(result)

# Different implementations
class SSHExecutor:
    def execute(self, cmd): ...

class KubeAPIExecutor:
    def execute(self, cmd): ...
```

**Benefits:**
- Swap implementations without changing callers
- Test with mock executors
- Multiple teams can provide their own executors

**When to Use:**
- When multiple implementations are likely
- When testing needs to be isolated
- When teams might have different patterns

---

### 3. Configuration as Data

**Principle:** Decisions in files, not code.

**Bad (Hardcoded):**
```python
ALLOWED_CLUSTERS = ["staging", "production", "shared-service"]
KUBECTL_USER = "stephen.tan"
REQUIRES_SUDO = True
```

**Good (Externalized):**
```yaml
# config/team-infrastructure.yaml
clusters:
  - staging
  - production
  - shared-service

kubernetes:
  access_method: ssh
  user: stephen.tan
  requires_sudo: true
```

```python
# Code reads configuration
config = yaml.load("config/team-infrastructure.yaml")
ALLOWED_CLUSTERS = config["clusters"]
```

**Benefits:**
- Teams can provide their own config without forking code
- Easy to test with different configurations
- Clear boundary between logic and data
- Other teams just replace the YAML file

**What Should Be Configuration:**
- ✅ Cluster names and URLs
- ✅ Node names and patterns
- ✅ Access methods (SSH vs kube API)
- ✅ Authentication details
- ❌ Core logic and algorithms
- ❌ Error handling patterns

---

### 4. Composition Over Inheritance

**Principle:** Build complex tools by combining simple ones.

**Bad (Deep Inheritance):**
```python
class TeleportTool:
    def authenticate(self): ...

class KubernetesTool(TeleportTool):
    def kubectl(self, cmd): ...

class FluxTool(KubernetesTool):
    def list_kustomizations(self): ...
    
# Problem: FluxTool inherits everything from TeleportTool
# Changing TeleportTool can break FluxTool
```

**Good (Composition):**
```python
class FluxTool:
    def __init__(self, teleport, kubernetes):
        self.teleport = teleport  # Dependency injection
        self.kubernetes = kubernetes
    
    def list_kustomizations(self):
        self.teleport.authenticate()
        return self.kubernetes.kubectl("get kustomizations")

# Usage
teleport = TeleportAuthenticator()
kubernetes = KubernetesClient(teleport)
flux = FluxTool(teleport, kubernetes)
```

**Benefits:**
- Clear dependency graph
- Easy to swap components
- Can mix and match implementations
- Easier to test (mock dependencies)

**When to Use:**
- Always prefer composition
- Only use inheritance for true "is-a" relationships
- In MCP servers, composition is almost always better

---

### 5. Dependency Inversion

**Principle:** High-level modules depend on abstractions, not low-level details.

**Traditional (Bad):**
```
High-level (Team Layer)
    ↓ depends on
Low-level (Platform Layer)
```

**Inverted (Good):**
```
High-level (Team Layer)
    ↓ depends on
Interface/Contract
    ↑ implements
Low-level (Platform Layer)
```

**Example:**
```python
# Define interface (abstraction)
class RemoteExecutor:
    def execute(self, cluster, node, command):
        raise NotImplementedError

# Platform layer implements interface
class TeleportSSHExecutor(RemoteExecutor):
    def execute(self, cluster, node, command):
        return run_remote_command(cluster, node, command)

# Team layer depends on abstraction
class FluxManager:
    def __init__(self, executor: RemoteExecutor):
        self.executor = executor  # Depends on interface, not implementation
```

**Benefits:**
- Platform layer can change without breaking team layer
- Multiple implementations can coexist
- Easy to test with mock implementations

---

### 6. Single Responsibility Principle

**Principle:** Each tool does ONE thing well.

**Bad (Swiss Army Knife):**
```python
def manage_flux(action, cluster, node, name=None, namespace=None, tail=None):
    if action == "list":
        return list_kustomizations(cluster, node)
    elif action == "suspend":
        return suspend_kustomization(cluster, node, name, namespace)
    elif action == "resume":
        return resume_kustomization(cluster, node, name, namespace)
    elif action == "logs":
        return get_logs(cluster, node, tail)
    # ... 10 more actions
```

**Good (Focused Tools):**
```python
@mcp.tool()
def list_flux_kustomizations(cluster: str, node: str):
    """List all Flux kustomizations."""
    ...

@mcp.tool()
def suspend_flux_kustomization(cluster: str, node: str, name: str, namespace: str):
    """Suspend a specific kustomization."""
    ...

@mcp.tool()
def resume_flux_kustomization(cluster: str, node: str, name: str, namespace: str):
    """Resume a suspended kustomization."""
    ...
```

**Benefits:**
- Easy to understand what each tool does
- Easy to test individually
- Easy to replace or deprecate one tool
- Clear naming and documentation

**How to Know If a Tool Has Too Many Responsibilities:**
- Uses "and" in description? ("List AND filter AND transform")
- Has multiple conditional branches based on mode/action?
- Documentation needs multiple sections?
- Hard to name clearly?

---

### 7. Open/Closed Principle

**Principle:** Open for extension, closed for modification.

**What This Means:**
- Can add new features without changing existing code
- Existing functionality is stable
- Extensions don't break existing users

**Examples:**

✅ **Adding a new layer:**
```
Platform (unchanged)
Team (unchanged)
Personal (unchanged)
New: Observability Layer (added without modifying others)
```

✅ **Adding a new tool:**
```python
# Existing tools unchanged
list_flux_kustomizations()  # Works as before

# New tool added
@mcp.tool()
def get_flux_alert_history():  # New functionality
    ...
```

✅ **Adding a new workflow:**
```markdown
META-WORKFLOWS.md
├─ MW-001: Thread Ending (unchanged)
├─ MW-002: New Tool Dev (unchanged)
└─ MW-009: New workflow (added)
```

**How to Design for Extension:**
- Use plugin patterns
- Accept configuration files
- Define clear extension points
- Document how to add new capabilities

---

## MCP-Specific Patterns

### Tool Independence

**Principle:** Tools should not assume other tools exist.

**Bad:**
```python
def advanced_flux_tool():
    # Assumes list_flux_kustomizations exists
    kustomizations = list_flux_kustomizations()
    ...
```

**Good:**
```python
def advanced_flux_tool(executor):
    # Uses primitive directly
    result = executor.execute("kubectl get kustomizations")
    kustomizations = parse(result)
    ...
```

**Why:** Tools might be used in different MCP servers, cherry-picked, or replaced.

---

### Resource Self-Containment

**Principle:** Resources should be complete and standalone.

**Bad:**
```yaml
# workflows/team/flux-workflows.md
"See platform-workflows.md for prerequisites"
```

**Good:**
```yaml
# workflows/team/flux-workflows.md
prerequisites:
  - Teleport authentication (platform layer)
  - SSH access to nodes (platform layer)
  - kubectl available on nodes

full_workflow:
  - Step 1: ...
  - Step 2: ...
```

**Why:** Resources might be read in isolation, out of context, or by external tools.

---

### Layer Contracts

**Principle:** Each layer exposes a clear contract.

**Platform Layer Contract:**
```yaml
provides:
  - authentication: Teleport SSO
  - remote_execution: SSH to any node
  - node_discovery: List available nodes

requires:
  - config/clusters.yaml
  - Valid Teleport credentials

guarantees:
  - Input validation (no shell injection)
  - Timeout protection
  - Clear error messages
```

**Team Layer Contract:**
```yaml
requires:
  - platform.authentication
  - platform.remote_execution

provides:
  - kubernetes_access: kubectl via SSH
  - flux_management: Flux GitOps operations

guarantees:
  - Uses platform primitives only
  - No direct infrastructure assumptions
  - Configurable via team-infrastructure.yaml
```

---

## State Management Principles

### Transient vs Persistent

**Principle:** Separate volatile state from permanent state.

**Transient (Not in Git):**
- Working notes
- Test output
- Current session state
- "Try this next" notes

**Location:** `.ephemeral/` (gitignored)

**Persistent (In Git):**
- Architecture decisions
- Completed features
- Lessons learned
- Stable documentation

**Location:** `docs/sessions/*/FINAL-SUMMARY.md`

**Analogy:**
```
Computer          MCP Server
──────────────────────────────
ROM               Git repository
RAM               .ephemeral/
Swap file         .state/
```

---

## Testing for Decoupling

### Can You Answer "Yes" to These?

✅ **Layer Independence:**
- Can you replace team layer without changing platform?
- Can personal layer work with different team implementations?

✅ **Tool Independence:**
- Can you use a single tool in isolation?
- Can you test a tool without real infrastructure?

✅ **Configuration Independence:**
- Can another team use this with just a config file change?
- Can you test with different configs without code changes?

✅ **Extension Without Modification:**
- Can you add a new workflow without changing existing ones?
- Can you add a new tool without modifying old tools?

✅ **Multi-Team Support:**
- Can Team B use platform layer as-is?
- Can Team B replace team layer without forking platform?

---

## Future-Proofing Checklist

**Before adding ANY new feature, ask:**

### Configuration
- [ ] Is this configuration or code?
- [ ] Can it be externalized to a YAML/JSON file?
- [ ] Will other teams need different values?

### Dependencies
- [ ] What does this depend on?
- [ ] Does it depend on abstractions or implementations?
- [ ] Can dependencies be injected?

### Composition
- [ ] Can this be built from existing primitives?
- [ ] Is this doing one thing or many things?
- [ ] Would composition be clearer than inheritance?

### Layer Placement
- [ ] Which layer does this belong to?
- [ ] Does it make assumptions about team infrastructure?
- [ ] Could it be more universal?

### Testing
- [ ] Can this be tested in isolation?
- [ ] Can I mock the dependencies?
- [ ] Does it require real infrastructure?

### Team Portability
- [ ] Will other teams need to modify this?
- [ ] Can they replace it with their own version?
- [ ] Is the interface clear and stable?

---

## Red Flags (Anti-Patterns)

### 🚩 Hardcoded Infrastructure Details
```python
# BAD
NODE_NAME = "pi-k8-staging"
```

**Fix:** Move to configuration file.

---

### 🚩 Deep Inheritance Hierarchies
```python
# BAD
class FluxTool(KubernetesTool(TeleportTool)):
```

**Fix:** Use composition and dependency injection.

---

### 🚩 God Tools (Do Everything)
```python
# BAD
def manage_everything(action, target, ...):
    if action == ...:
```

**Fix:** Split into focused, single-purpose tools.

---

### 🚩 Tight Coupling Between Layers
```python
# BAD - Team tool directly imports platform implementation
from platform_layer import _internal_ssh_command
```

**Fix:** Use public interfaces only, pass dependencies.

---

### 🚩 Assumptions About Other Tools
```python
# BAD
def my_tool():
    # Assumes list_flux_kustomizations exists
    data = list_flux_kustomizations()
```

**Fix:** Accept data as parameter or use primitive directly.

---

### 🚩 Mixed Transient and Persistent State
```markdown
# BAD - In git
## Session Summary
- Completed: Tool X
- Testing: Tool Y (WIP)
- Next: Try Z
```

**Fix:** Transient → `.ephemeral/`, Persistent → `docs/sessions/`

---

## Evolution Strategy

### When Requirements Change

**Process:**
1. **Identify the change:** What assumption was wrong?
2. **Find the abstraction boundary:** Which layer is affected?
3. **Check the interface:** Can we change implementation without breaking interface?
4. **Update configuration first:** Can this be a config change instead of code?
5. **Extend, don't modify:** Can we add rather than change?

**Example: 3-Cluster Architecture Discovery**

```
Change: K8s runs in shared-service cluster, not production
├─ Layer affected: Platform (cluster configuration)
├─ Interface impact: None (still uses same Teleport auth)
├─ Solution: Add cluster to config, update documentation
└─ Code changes: Minimal (just cluster list)
```

---

## Measuring Success

### Metrics for Decoupling

**Good Signs:**
- ✅ New team can adopt platform layer without changes
- ✅ Can add tools without modifying existing ones
- ✅ Tests run without real infrastructure
- ✅ Configuration changes don't require code changes
- ✅ Layers can be versioned independently

**Warning Signs:**
- ⚠️ Every new feature requires changes across multiple layers
- ⚠️ Tests require full infrastructure setup
- ⚠️ Other teams need to fork the entire codebase
- ⚠️ Hard to explain what a tool does
- ⚠️ Frequent merge conflicts in same files

---

## Summary

**The Goal:** Build a system that can evolve as we discover new requirements.

**The Strategy:**
1. **Separate concerns** (layers, tools, workflows, state)
2. **Depend on interfaces** (not implementations)
3. **Configure via data** (not hardcoded)
4. **Compose from primitives** (not deep hierarchies)
5. **One responsibility per tool** (focus)
6. **Extend, don't modify** (stability)

**The Test:** Can another team use this with minimal changes?

**The Practice:** Before adding anything, run the Future-Proofing Checklist.

**The Mindset:** Assume our assumptions are wrong. Design for change.

---

## Related Documents

- `resources/rules/design-checklist.yaml` - **Structured rules (MCP Resource)** - Actionable version of these principles
- `ROADMAP.md` - Migration plan and target architecture
- `resources/architecture/layer-model.yaml` - 3-layer dependency model
- `docs/sessions/*/FINAL-SUMMARY.md` - Lessons learned from practice
- `META-WORKFLOWS.md` - Process patterns (orthogonal to these principles)

## This Document vs design-checklist.yaml

**This Document (DESIGN-PRINCIPLES.md):**
- Comprehensive explanations and reasoning
- Teaching by example and analogy
- Context for WHY principles matter
- For humans reading and learning

**design-checklist.yaml Resource:**
- Structured, parseable rules
- Actionable checklists and red flags
- For AI runtime validation during tool development
- Concise, targeted, programmatic

Both serve different purposes - this teaches, the resource enforces.

---

**Remember:** These are principles, not rules. Use judgment. Sometimes a simple hardcoded solution is fine. The goal is to make intentional decisions about coupling, not to achieve perfect decoupling everywhere.

When in doubt: **Make it work, make it right, make it fast** - in that order.