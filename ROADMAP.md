# Platform MCP Server - Roadmap & Architecture Vision

**Status:** Planning Document  
**Created:** 2024-01-07  
**Last Updated:** 2024-01-07

---

## Overview

This document outlines the planned evolution of the Platform MCP Server from a single-user, single-team tool into a modular, multi-team platform that separates universal patterns from team-specific and personal implementations.

---

## Current State (V1c)

### Architecture
```
platform-mcp-server/
├── README.md                    # Mixed documentation
├── META-WORKFLOWS.md            # Mixed universal + personal workflows
├── SESSION-SUMMARY-V1c.md       # Session continuation docs
├── platform_mcp.py              # All tools in one file
├── requirements.txt             # Python dependencies
└── test_*.py                    # Test scripts
```

### Problems Identified

1. **File Structure Confusion**
   - `META-WORKFLOWS.md` in root looks like user documentation, but it's an MCP resource
   - No clear separation between docs for humans vs data for AI

2. **Mixed Abstraction Levels**
   - Universal patterns (meta-workflows concept) mixed with personal workflows (ansible-mac)
   - Platform tools (Teleport) mixed with team tools (Flux) mixed with personal tools (Zed config)
   - Hard for other teams to adopt without forking everything

3. **Unclear Dependencies**
   - Which tools depend on what infrastructure?
   - Can't easily identify "this is universal" vs "this is team-specific"
   - Documentation doesn't make architectural boundaries explicit

4. **Transient vs Persistent State Confusion**
   - `SESSION-SUMMARY-V1c.md` contains BOTH completed work AND current WIP
   - Gets committed to git while constantly changing
   - Mixes "RAM-like" transient state with "ROM-like" persistent documentation
   - No clear place for working notes, test results, or session scratchpad
   - Creates "should I commit this?" ambiguity

---

## Target State (V2.0)

### The 3-Layer Architecture Model

**Key Insight:** This is a **dependency graph**, not a strict hierarchy.

```
┌─────────────────────────────────────────────────┐
│  LAYER 1: PLATFORM (Organization-wide)          │
│  - Teleport authentication                      │
│  - SSH primitives                               │
│  - Core security                                │
│  - Anyone at company can use                    │
└─────────────────────────────────────────────────┘
         ↓ depends on              ↓
┌──────────────────────┐    ┌────────────────────┐
│ LAYER 2: TEAM        │    │ LAYER 3: PERSONAL  │
│ - SSH-based K8s      │    │ - ansible-mac      │
│ - Flux via SSH       │    │ - Zed config       │
│ - Team patterns      │    │ - Laptop setup     │
└──────────────────────┘    └────────────────────┘
         ↓ depends on              ↑
         └──────────────────────────┘
          (Personal can depend on
           Platform OR Team)
```

### Proposed File Structure

```
platform-mcp-server/
├── docs/                                    # Human-readable documentation
│   ├── README.md                           # Main documentation
│   ├── MCP-CONCEPTS.md                     # Tools vs Resources explained
│   ├── CONTRIBUTING.md                     # How to contribute
│   ├── DESIGN-PRINCIPLES.md                # Decoupling & evolution principles
│   └── sessions/                           # Session summaries (persistent only)
│       └── V1c/
│           ├── FINAL-SUMMARY.md            # Completed work, lessons learned
│           ├── ARCHITECTURE.md             # Architecture decisions
│           └── TOOLS-IMPLEMENTED.md        # Tool documentation
│
├── resources/                               # MCP Resources (AI reads these)
│   ├── architecture/
│   │   ├── layer-model.yaml                # 3-layer dependency model ✅ CREATED
│   │   └── infrastructure-map.yaml         # Current infrastructure map
│   │
│   └── workflows/
│       ├── universal/                      # Any team can use
│       │   ├── meta-workflows.md           # Universal patterns
│       │   └── README.md                   # What makes these universal
│       │
│       ├── team/                           # Our team's specific workflows
│       │   ├── flux-workflows.md           # Flux-specific processes
│       │   ├── ssh-k8s-workflows.md        # SSH K8s patterns
│       │   └── README.md                   # Team context
│       │
│       └── personal/                       # Individual-specific
│           ├── stephen-workflows.md        # Your personal workflows
│           ├── stephen-infrastructure.yaml # Your laptop/environment
│           └── README.md                   # Personal context
│
├── src/                                     # Source code
│   ├── platform_mcp.py                     # Main MCP server
│   ├── layers/
│   │   ├── platform.py                     # Platform layer tools
│   │   ├── team.py                         # Team layer tools
│   │   └── personal.py                     # Personal layer tools
│   │
│   └── utils/
│       ├── security.py                     # Input validation, shlex
│       └── teleport.py                     # Teleport helpers
│
├── tests/                                   # Test suite
│   ├── test_platform_layer.py
│   ├── test_team_layer.py
│   └── test_personal_layer.py
│
├── config/
│   ├── teleport_clusters.yaml              # Cluster configuration
│   └── layer_config.yaml                   # Layer-specific config
│
├── requirements.txt                         # Python dependencies
├── .ephemeral/                              # Transient state (NOT in git)
│   ├── working-notes.md                    # Session scratchpad
│   ├── test-results.log                    # Test output
│   ├── next-actions.md                     # TODOs
│   └── current-state.json                  # Machine-readable state
│
├── .gitignore                              # Ignore transient state
│   ├── .ephemeral/
│   ├── .state/
│   └── *.WORKING.md
│
├── ROADMAP.md                              # This file
└── CHANGELOG.md                            # Version history
```

---

## State Management Strategy

### The Problem: Transient vs Persistent State

**Current Issue:** `SESSION-SUMMARY-V1c.md` acts like RAM (constantly changing) but lives in git (permanent storage).

**The Conflict:**
```
Session Summary Contains:
├─ Persistent: Architecture decisions, lessons learned ← Should be in git
└─ Transient: "Testing X now", "Try Y next", WIP notes ← Shouldn't be in git!
```

**Computer Architecture Analogy:**
| Type | Computer | MCP Server | Git? |
|------|----------|------------|------|
| Permanent | ROM/Disk | Completed docs | ✅ Yes |
| Volatile | RAM | Working notes | ❌ No |
| Temporary | Swap file | Session state | ❌ No |
| Fast access | Cache | Checkpoints | ❌ No |

### The Solution: Separate Storage

#### Persistent State (Git-Tracked)

**Location:** `docs/sessions/V1c/FINAL-SUMMARY.md`

**Contents:**
- Architecture decisions
- Lessons learned
- Completed features
- Stable tool documentation
- Patterns discovered

**Committed:** At session end (via MW-001)

#### Transient State (Local Only)

**Location:** `.ephemeral/` directory (in `.gitignore`)

**Contents:**
- `working-notes.md` - Scratchpad, thoughts, WIP notes
- `test-results.log` - Test output, debugging info
- `next-actions.md` - Immediate TODOs
- `current-state.json` - Machine-readable session state

**Never committed:** Cleared or archived at session end

### Workflow Integration

#### During Session (Use Transient State)
```bash
# Scratchpad notes (not tracked)
echo "Testing MW-008 trigger phrases" >> .ephemeral/working-notes.md
echo "Issue: regex not matching" >> .ephemeral/working-notes.md
echo "Fixed: Updated pattern" >> .ephemeral/working-notes.md

# Next actions (not tracked)
echo "- Test on shared-service cluster" >> .ephemeral/next-actions.md
echo "- Update documentation" >> .ephemeral/next-actions.md

# Session state (not tracked)
{
  "session_id": "v1c-20240107",
  "current_task": "Testing MW-008",
  "completed": ["3-cluster-discovery", "MW-008-creation"],
  "pending": ["test-remaining-v1c-tools"]
}
```

#### End of Session (Extract & Persist)

**Via MW-001 (Thread Ending Summary):**
1. Read `.ephemeral/working-notes.md`
2. Extract key learnings → `docs/sessions/V1c/FINAL-SUMMARY.md`
3. Commit persistent docs only
4. Clear or archive `.ephemeral/`

```bash
# Review transient state
cat .ephemeral/working-notes.md

# Extract permanent lessons
# → "MW-008 needs exact trigger wording"
# → Add to docs/sessions/V1c/FINAL-SUMMARY.md

# Commit persistent docs only
git add docs/sessions/
git commit -m "Session V1c complete: 3-layer architecture defined"

# Transient state stays local (or gets cleared)
rm -rf .ephemeral/*  # Optional - can keep for continuation
```

### Benefits

✅ **No more "should I commit this?" confusion**
- Transient notes go in `.ephemeral/` (never committed)
- Permanent learnings go in `docs/sessions/` (committed at end)

✅ **Can be messy during session**
- Working notes can be rough, incomplete
- Only polished output goes to git

✅ **Session continuation support**
- Keep `.ephemeral/` intact between sessions
- Pick up exactly where you left off

✅ **Clean git history**
- Only completed, stable artifacts in git
- No "WIP" or "testing..." commits

---

## Migration Plan

### Phase 1: Documentation & Resource Structure (Next Session)

**Goal:** Make the architecture explicit without breaking existing functionality

**Tasks:**
- [x] Create `resources/architecture/layer-model.yaml` ✅
- [x] Create `ROADMAP.md` ✅
- [x] Create `docs/MCP-CONCEPTS.md` (Tools vs Resources for newbies) ✅
- [x] Move `DESIGN-PRINCIPLES.md` → `docs/DESIGN-PRINCIPLES.md` ✅
- [x] Create `.ephemeral/` directory structure ✅
- [x] Update `.gitignore` to exclude transient state ✅
- [x] Move `SESSION-SUMMARY-V1c.md` → `docs/sessions/V1c/FINAL-SUMMARY.md` ✅
- [x] Update README to reference new structure ✅
- [x] Update MW-001 to handle transient → persistent extraction ✅
- [ ] Create `resources/workflows/` directory structure
- [ ] Split `META-WORKFLOWS.md` into universal/team/personal sections

**Success Criteria:**
- New structure documented and committed
- No code changes yet (safe)
- Clear separation of transient vs persistent state
- Clear migration path established

### Phase 2: Code Reorganization (Future Session)

**Goal:** Separate tools by layer in code

**Tasks:**
- [ ] Create `src/layers/platform.py` - Extract V1a, V1b tools
- [ ] Create `src/layers/team.py` - Extract V1c Flux tools
- [ ] Create `src/layers/personal.py` - Extract deployment workflows
- [ ] Update `platform_mcp.py` to import from layers
- [ ] Create layer-specific test files
- [ ] Update MCP resource paths

**Success Criteria:**
- All tools still work
- Clear layer boundaries in code
- Easy to identify tool dependencies

### Phase 3: Multi-Team Support (Future)

**Goal:** Make it easy for other teams to fork and adapt

**Tasks:**
- [ ] Create team configuration system
- [ ] Make team layer pluggable
- [ ] Create example "Team B" configuration
- [ ] Document forking process
- [ ] Create team onboarding guide

**Success Criteria:**
- Other teams can use platform layer as-is
- Easy to replace team layer with their patterns
- Clear documentation for forking

---

## Benefits of This Architecture

### For Current Use (Single User/Team)

1. **Clarity**
   - Clear boundaries between universal, team, personal
   - Easier to understand dependencies
   - Better documentation organization

2. **Maintainability**
   - Changes to team patterns don't affect platform tools
   - Personal workflows isolated from shared tools
   - Easier to test layers independently

3. **Evolution**
   - Can add new layers without breaking existing ones
   - Can version layers independently
   - Clear upgrade paths

### For Future Multi-Team Use

1. **Reusability**
   - Other teams keep platform layer (Teleport, SSH)
   - Replace team layer with their patterns (ArgoCD instead of Flux)
   - Each developer has their own personal layer

2. **Modularity**
   - Teams can mix and match layers
   - Platform layer becomes organization-wide standard
   - Teams innovate on team layer independently

3. **Collaboration**
   - Universal patterns shared across teams
   - Team-specific patterns documented and shareable
   - Personal workflows don't pollute shared code

---

## Orthogonality: Layers vs Workflows

**Important:** Layers and Workflows are **orthogonal concepts** that work together:

### Layers (This Document)
- **What:** Capabilities and dependencies
- **Question:** "What tools exist and what do they depend on?"
- **Document:** `resources/architecture/layer-model.yaml`
- **Example:** "list_flux_kustomizations is a team layer tool that depends on platform layer's run_remote_command"

### Workflows (META-WORKFLOWS.md)
- **What:** Multi-step processes
- **Question:** "How do I execute this complex task?"
- **Document:** `resources/workflows/*/meta-workflows.md`
- **Example:** "MW-004 Deploy MCP Changes uses tools from platform, team, and personal layers"

### How They Work Together

A workflow (process) uses tools from multiple layers (capabilities):

```
MW-004: Deploy MCP Changes
├─ Step 1: Commit code      → Platform layer (git)
├─ Step 2: Push to GitHub   → Platform layer (git)
├─ Step 3: Sync with Ansible → Personal layer (ansible-mac)
├─ Step 4: Restart Zed      → Personal layer (Zed config)
└─ Step 5: Verify           → Team layer (Flux tools)
```

---

## Resource Definitions

### MCP Resources (AI Reads These)

| Resource Path | File | Purpose |
|---------------|------|---------|
| `layer-model://architecture` | `resources/architecture/layer-model.yaml` | 3-layer dependency model |
| `workflow://universal` | `resources/workflows/universal/meta-workflows.md` | Universal workflow patterns |
| `workflow://team` | `resources/workflows/team/flux-workflows.md` | Team-specific workflows |
| `workflow://personal` | `resources/workflows/personal/stephen-workflows.md` | Personal workflows |
| `workflow://all` | Combined view of all workflows | Aggregated workflow view |

### MCP Tools (AI Executes These)

Organized by layer:

**Platform Layer:**
- `check_tsh_installed()`, `get_tsh_client_version()`, etc.
- `list_teleport_nodes()`, `verify_ssh_access()`, `run_remote_command()`

**Team Layer:**
- `list_flux_kustomizations()`, `reconcile_flux_kustomization()`, etc.
- `list_flux_sources()`, `get_flux_logs()`, etc.

**Personal Layer:**
- Deployment automation (git + ansible + zed restart)
- Local environment verification

---

## Implementation Notes

### Backward Compatibility

**Critical:** All existing functionality must continue to work during migration.

**Strategy:**
1. Phase 1: Add new structure alongside old (no breaking changes)
2. Phase 2: Refactor code to use layers internally (external API unchanged)
3. Phase 3: Deprecate old paths with warnings, document new paths

### MCP Resource Updates

When moving files, update MCP resources:

```python
# Old (V1c)
@mcp.resource("workflow://meta-workflows")
async def get_meta_workflows() -> str:
    with open("META-WORKFLOWS.md") as f:
        return f.read()

# New (V2.0)
@mcp.resource("workflow://universal")
async def get_universal_workflows() -> str:
    with open("resources/workflows/universal/meta-workflows.md") as f:
        return f.read()

@mcp.resource("workflow://team")
async def get_team_workflows() -> str:
    with open("resources/workflows/team/flux-workflows.md") as f:
        return f.read()

@mcp.resource("layer-model://architecture")
async def get_layer_model() -> str:
    with open("resources/architecture/layer-model.yaml") as f:
        return f.read()
```

---

## Examples: Other Teams Using This

### Team A (Current - Platform Team)

```yaml
platform:
  - Teleport auth ✓
  - SSH primitives ✓

team:
  - SSH-based K8s access
  - Flux GitOps
  - 3-cluster architecture (staging/production/shared-service)

personal:
  - ansible-mac
  - Zed editor
```

### Team B (Hypothetical - Application Team)

```yaml
platform:
  - Teleport auth ✓ (SAME!)
  - SSH primitives ✓ (SAME!)

team:
  - Direct kube API access (DIFFERENT!)
  - ArgoCD GitOps (DIFFERENT!)
  - 2-cluster architecture (dev/prod)

personal:
  - Homebrew
  - VS Code
```

**Result:** Team B can reuse Platform layer entirely, replace Team layer, use their own Personal layer.

---

## Success Metrics

### Phase 1 (Documentation) Complete When:
- [ ] All resources properly organized
- [ ] Layer model documented
- [ ] Clear separation visible in file structure
- [ ] No functionality broken

### Phase 2 (Code) Complete When:
- [ ] Tools organized by layer in code
- [ ] All tests passing
- [ ] Layer dependencies explicit
- [ ] Can easily identify tool boundaries

### Phase 3 (Multi-Team) Complete When:
- [ ] Example team configuration exists
- [ ] Forking process documented
- [ ] Another team successfully adopts platform layer
- [ ] Clear onboarding guide

---

## Open Questions

1. **Tool Discovery:** Should we add a `list_tools_by_layer()` tool?
2. **Layer Validation:** Should tools validate their layer dependencies at runtime?
3. **Configuration:** Should layer config be in YAML or Python?
4. **Testing:** How to test multi-team scenarios without multiple infrastructures?
5. **Versioning:** Should layers have independent version numbers?

---

## Architectural Principles for Evolution

### The Core Question: "How do we guard against unknown future constraints?"

**Challenge:** We're making this up as we go, discovering requirements incrementally.

**Risk:** Painting ourselves into a corner with tightly-coupled designs.

**Solution:** Design principles that enable evolution without breaking existing functionality.

### Key Principles

#### 1. **Loose Coupling via Interfaces**

**Pattern:** Tools communicate through well-defined contracts, not implementations.

```python
# BAD: Direct coupling
def team_tool():
    result = run_remote_command(...)  # Directly depends on platform implementation

# GOOD: Interface coupling
def team_tool(executor):
    result = executor.run(...)  # Depends on interface, not implementation
```

**Benefits:**
- Can swap implementations without changing callers
- Platform layer can evolve without breaking team layer
- Easy to mock for testing

#### 2. **Configuration as Data (Not Code)**

**Pattern:** Keep decisions in data files (YAML/JSON), not hardcoded.

```python
# BAD: Hardcoded
ALLOWED_CLUSTERS = ["staging", "production", "shared-service"]

# GOOD: Externalized
config = yaml.load("config/clusters.yaml")
ALLOWED_CLUSTERS = config["clusters"]
```

**Benefits:**
- Teams can provide their own config without forking code
- Easier to test with different configurations
- Clear boundaries between logic and data

#### 3. **Composition Over Inheritance**

**Pattern:** Build complex tools by composing simple ones.

```python
# BAD: Deep inheritance
class FluxTool(KubernetesTool(TeleportTool)):
    ...

# GOOD: Composition
class FluxTool:
    def __init__(self, teleport, kubernetes):
        self.teleport = teleport
        self.kubernetes = kubernetes
```

**Benefits:**
- Easier to change dependencies
- Can mix and match components
- Clearer dependency graph

#### 4. **Dependency Inversion**

**Pattern:** High-level tools depend on abstractions, not low-level details.

```
Platform Layer (abstractions)
    ↑ depends on interface
Team Layer (implements interface)
```

**Benefits:**
- Can replace team layer without changing platform
- Multiple implementations of same interface
- Testable in isolation

#### 5. **Single Responsibility (Tools Do One Thing)**

**Pattern:** Each tool has one clear purpose.

```python
# BAD: Swiss army knife
def manage_flux(action, cluster, node, ...):
    if action == "list": ...
    elif action == "suspend": ...
    elif action == "resume": ...
    elif action == "logs": ...

# GOOD: Focused tools
def list_flux_kustomizations(...): ...
def suspend_flux_kustomization(...): ...
def resume_flux_kustomization(...): ...
def get_flux_logs(...): ...
```

**Benefits:**
- Easy to understand
- Easy to test
- Easy to replace individually

#### 6. **Open/Closed Principle**

**Pattern:** Open for extension, closed for modification.

```python
# Can add new layers without modifying existing ones
# Can add new tools without changing old tools
# Can add new workflows without changing architecture
```

### Applying to MCP Server

#### Layer Boundaries = Interfaces

```yaml
# Platform layer contract
platform_interface:
  provides:
    - authentication (Teleport)
    - remote_execution (SSH)
  
  expects_from_teams:
    - config/clusters.yaml
    - config/nodes.yaml

# Team layer contract  
team_interface:
  requires:
    - platform.authentication
    - platform.remote_execution
  
  provides:
    - kubernetes_access
    - flux_management
```

#### Resources = Data-Driven

```
resources/
├── architecture/layer-model.yaml    ← Data (not code)
├── workflows/universal/*.md         ← Data (not code)
└── configuration/*.yaml             ← Data (not code)

# Code just reads and interprets these
```

#### Tools = Composable

```python
# Primitive
run_remote_command(cluster, node, cmd)

# Composed from primitive
list_flux_kustomizations(cluster, node):
    return run_remote_command(cluster, node, "kubectl get kustomizations")

# Composed from composed
get_failing_kustomizations(cluster, node):
    all_kustomizations = list_flux_kustomizations(cluster, node)
    return [k for k in all_kustomizations if k.ready == "False"]
```

### Validation Strategy

**How to check if we're staying decoupled:**

✅ **Can we swap layers?**
- Replace team layer with different K8s access pattern?
- Replace personal layer with different laptop setup?

✅ **Can we add without breaking?**
- Add new workflow without changing existing ones?
- Add new tool without modifying old tools?

✅ **Can we test independently?**
- Test team tools without real Teleport infrastructure?
- Test workflows without real clusters?

✅ **Can teams fork easily?**
- Other team takes platform layer as-is?
- Other team replaces only team layer?

### Future-Proofing Checklist

Before adding new features, ask:

- [ ] Is this configuration or code? (Prefer configuration)
- [ ] Does it depend on abstractions or implementations? (Prefer abstractions)
- [ ] Can it be composed from existing primitives? (Prefer composition)
- [ ] Does it have a single, clear responsibility? (Prefer focused)
- [ ] Can it be tested in isolation? (Prefer testable)
- [ ] Will other teams need to modify it? (Prefer not)

---

## Related Documents

- `resources/architecture/layer-model.yaml` - Detailed layer architecture
- `docs/DESIGN-PRINCIPLES.md` - Full decoupling guidelines (to be created)
- `META-WORKFLOWS.md` - Current workflow documentation (to be split)
- `docs/sessions/V1c/` - Session history and context (to be created)
- `README.md` - User-facing documentation (to be updated)

---

## Conclusion

This roadmap transforms the Platform MCP Server from a single-user tool into a modular platform that:
- Makes architectural boundaries explicit
- Enables multi-team adoption
- Preserves backward compatibility
- Creates clear separation of concerns
- Separates transient state from persistent documentation
- Provides principles for evolution without breaking changes

The 3-layer model (Platform → Team → Personal) provides a clear mental model for understanding tool dependencies and enables teams to reuse universal patterns while implementing their own specific workflows.

The state management strategy (persistent vs transient) ensures clean git history and clear working boundaries.

The design principles (loose coupling, composition, dependency inversion) guard against unknown future constraints by keeping the architecture flexible and evolvable.

**Next Step:** Execute Phase 1 (Documentation & Resource Structure) in the next session.