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
│   └── sessions/                           # Session summaries
│       └── SESSION-SUMMARY-V1c.md          # V1c session
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
├── ROADMAP.md                              # This file
└── CHANGELOG.md                            # Version history
```

---

## Migration Plan

### Phase 1: Documentation & Resource Structure (Next Session)

**Goal:** Make the architecture explicit without breaking existing functionality

**Tasks:**
- [x] Create `resources/architecture/layer-model.yaml` ✅
- [x] Create `ROADMAP.md` ✅
- [ ] Create `docs/MCP-CONCEPTS.md` (Tools vs Resources for newbies)
- [ ] Move `SESSION-SUMMARY-V1c.md` → `docs/sessions/`
- [ ] Create `resources/workflows/` directory structure
- [ ] Split `META-WORKFLOWS.md` into universal/team/personal sections
- [ ] Update README to reference new structure

**Success Criteria:**
- New structure documented and committed
- No code changes yet (safe)
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

## Related Documents

- `resources/architecture/layer-model.yaml` - Detailed layer architecture
- `META-WORKFLOWS.md` - Current workflow documentation (to be split)
- `SESSION-SUMMARY-V1c.md` - Session history and context
- `README.md` - User-facing documentation (to be updated)

---

## Conclusion

This roadmap transforms the Platform MCP Server from a single-user tool into a modular platform that:
- Makes architectural boundaries explicit
- Enables multi-team adoption
- Preserves backward compatibility
- Creates clear separation of concerns

The 3-layer model (Platform → Team → Personal) provides a clear mental model for understanding tool dependencies and enables teams to reuse universal patterns while implementing their own specific workflows.

**Next Step:** Execute Phase 1 (Documentation & Resource Structure) in the next session.