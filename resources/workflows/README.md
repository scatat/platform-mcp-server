# Workflow Organization

This directory contains organized meta-workflows for the Platform MCP Server.

## Structure

```
resources/workflows/
├── README.md           # This file
├── universal/          # Universal workflows (any team, any MCP server)
├── team/               # Team-specific workflows (Flux, K8s, our infrastructure)
└── personal/           # Personal workflows (ansible-mac, my setup)
```

## Workflow Categories

### Universal Workflows

**Location**: `universal/`

**Applies to**: Any MCP server development, any team, any infrastructure

**Examples**:
- MW-001: Thread Ending Summary
- MW-002: New MCP Tool Development
- MW-003: MCP Tool Testing Suite
- MW-005: Create New Meta-Workflow
- MW-008: Architectural Discovery & Correction

**Characteristics**:
- ✅ Infrastructure-agnostic
- ✅ Reusable across teams
- ✅ Core MCP development processes
- ✅ Can be adopted as-is by other teams

---

### Team Workflows

**Location**: `team/`

**Applies to**: This team's specific infrastructure (Flux, Kubernetes, Teleport)

**Examples**:
- MW-006: Flux Debugging Session

**Characteristics**:
- ⚙️ Team-specific tools (Flux, K8s)
- ⚙️ Our infrastructure patterns
- ⚙️ Can be replaced by other teams
- ⚙️ Requires our specific setup

**For Other Teams**:
If you fork this server, you can:
1. Keep `universal/` as-is
2. Replace `team/` with your workflows
3. Replace `personal/` with your setup

---

### Personal Workflows

**Location**: `personal/`

**Applies to**: Individual developer's personal setup and preferences

**Examples**:
- MW-004: Deploy MCP Changes (uses ansible-mac)

**Characteristics**:
- 👤 Personal tooling (ansible-mac)
- 👤 Individual preferences
- 👤 Local machine setup
- 👤 Won't apply to other developers

---

## How Workflows Are Stored

Currently, all workflows are documented in the root-level `META-WORKFLOWS.md` file.

**Why not separate files yet?**

We're taking an **incremental approach**:

1. **Phase 1 (Current)**: Document the organization structure
   - Create directory structure
   - Explain categorization
   - Add section headers to META-WORKFLOWS.md

2. **Phase 2 (Future)**: Extract to separate files
   - Move each workflow to its category directory
   - Keep META-WORKFLOWS.md as index/registry
   - Add MCP resources for individual workflows

**Benefits of this approach**:
- ✅ Easy discovery (single file for now)
- ✅ Clear categorization (sections in file)
- ✅ Migration path documented
- ✅ No breaking changes yet

---

## Workflow Registry

The canonical registry is maintained in the root `META-WORKFLOWS.md` file.

**Current Workflows** (as of 2024-01-07):

| ID | Name | Category | Status |
|----|------|----------|--------|
| MW-001 | Thread Ending Summary | Universal | Active |
| MW-002 | New MCP Tool Development | Universal | Active |
| MW-003 | MCP Tool Testing Suite | Universal | Active |
| MW-005 | Create Meta-Workflow | Universal | Active |
| MW-008 | Architectural Discovery & Correction | Universal | Active |
| MW-006 | Flux Debugging Session | Team | Draft |
| MW-004 | Deploy MCP Changes | Personal | Active |
| MW-007 | New Tool Category | Universal | Draft |

---

## For Multi-Team Adoption

If you're another team adopting this MCP server:

### Keep Universal Workflows
```bash
# These apply to any MCP development
resources/workflows/universal/
├── MW-001-thread-ending.md
├── MW-002-new-tool.md
├── MW-003-testing.md
├── MW-005-create-workflow.md
└── MW-008-architectural-discovery.md
```

### Replace Team Workflows
```bash
# Replace our Flux/K8s workflows with yours
resources/workflows/team/
├── YOUR-team-specific-workflow-1.md
├── YOUR-team-specific-workflow-2.md
└── YOUR-infrastructure-patterns.md
```

### Replace Personal Workflows
```bash
# Use your own tooling
resources/workflows/personal/
├── YOUR-deployment-process.md
├── YOUR-local-setup.md
└── YOUR-preferences.md
```

---

## Migration Plan

### Phase 1: Documentation Structure (✅ Current)
- [x] Create directory structure
- [x] Document categorization
- [x] Add README explaining organization
- [x] Update META-WORKFLOWS.md with section headers

### Phase 2: File Extraction (Future)
- [ ] Extract each workflow to separate markdown file
- [ ] Update META-WORKFLOWS.md to reference separate files
- [ ] Add MCP resources for individual workflows
- [ ] Test workflow discovery still works

### Phase 3: MCP Resource Endpoints (Future)
- [ ] Add `workflow://workflows/universal/MW-001`
- [ ] Add `workflow://workflows/team/MW-006`
- [ ] Add `workflow://workflows/personal/MW-004`
- [ ] Update `list_meta_workflows()` to show categories

---

## Related Documentation

- **[META-WORKFLOWS.md](../../META-WORKFLOWS.md)** - Current workflow registry
- **[ROADMAP.md](../../ROADMAP.md)** - Phase 1 migration plan
- **[layer-model.yaml](../architecture/layer-model.yaml)** - 3-layer architecture

---

## Future Enhancements

### Smart Workflow Discovery
```python
# AI could filter by category
list_meta_workflows(category="universal")
# Returns only universal workflows

list_meta_workflows(category="team")
# Returns only team-specific workflows
```

### Workflow Composition
```python
# AI could chain workflows
execute_workflow("MW-002")  # New MCP Tool Development
  └─> calls MW-003           # Testing
      └─> calls MW-001       # Thread Ending Summary
```

### Custom Categories
```bash
# Teams could add their own categories
resources/workflows/
├── universal/
├── team/
├── personal/
└── experimental/  # Custom category
```

---

## Contributing

When creating a new workflow, ask:

1. **Is it universal?** (Any MCP server can use it)
   → Put in `universal/`

2. **Is it team-specific?** (Requires our infrastructure)
   → Put in `team/`

3. **Is it personal?** (Just my setup)
   → Put in `personal/`

See **MW-005: Create New Meta-Workflow** for the full process.