# Installation System Design

## Problem Statement

The Platform MCP Server currently assumes:
1. macOS operating system
2. ansible-mac for dependency installation
3. Specific hardcoded paths (`~/personal/git/ansible-mac`)

**Reality at Wise:**
- Multiple OS: macOS (Kandji MDM), Linux Ubuntu (Landscape)
- Multiple installation methods: brew, apt, ansible, manual
- Different team preferences and constraints
- MDM restrictions may prevent certain installation methods

**Result:** Hard for other teams to adopt. Installation instructions don't work for non-Mac users.

## Design Goals

1. **Loose Coupling**: Installation method ≠ MCP tool functionality
2. **OS Agnostic**: Works on macOS, Linux, potentially Windows
3. **MDM Aware**: Respects Kandji, Landscape, other management systems
4. **Flexible**: Support multiple installation methods simultaneously
5. **No Hardcoded Paths**: Configuration over convention
6. **Backward Compatible**: Existing setups continue working

## Core Principle: Separation of Concerns

```
┌─────────────────────────────────────────────────────┐
│  MCP Server (Runtime)                               │
│  - Executes tools                                   │
│  - Assumes dependencies are installed               │
│  - Doesn't care HOW they got installed              │
└─────────────────────────────────────────────────────┘
                      ↑
                      │ (uses)
                      │
┌─────────────────────────────────────────────────────┐
│  Dependencies (Installed)                           │
│  - tsh (Teleport CLI)                               │
│  - Python 3.11+                                     │
│  - kubectl (optional)                               │
│  - flux (optional)                                  │
└─────────────────────────────────────────────────────┘
                      ↑
                      │ (installed by)
                      │
┌─────────────────────────────────────────────────────┐
│  Installation System (Bootstrap)                    │
│  - Detects OS                                       │
│  - Detects MDM                                      │
│  - Guides user to correct install method            │
│  - Creates config files                             │
└─────────────────────────────────────────────────────┘
```

**Key Insight:** The MCP server should NEVER know about installation methods. It only checks if dependencies exist and provides guidance when they don't.

## Architecture

### Layer 1: Dependency Detection (Read-Only)

Tools detect what's installed, return status:

```python
def check_dependency(name: str) -> dict:
    """Check if a dependency is installed (OS-agnostic)"""
    return {
        "installed": bool,
        "version": str,
        "path": str,
        "message": str
    }
```

**Examples:**
- `check_tsh_installed()` ✅ (already exists)
- `check_kubectl_installed()` (new)
- `check_python_version()` (new)

### Layer 2: Installation Guidance (Configurable)

When dependencies are missing, return **generic guidance** that's OS-aware but not prescriptive:

```python
def get_install_guidance(dependency: str) -> dict:
    """Return installation guidance based on OS"""
    os_type = detect_os()  # macos, linux, windows
    
    return {
        "dependency": dependency,
        "os": os_type,
        "methods": {
            "recommended": "brew install teleport",  # OS-specific
            "alternatives": [
                "apt install teleport",
                "Download from https://goteleport.com/download"
            ]
        },
        "mdm_notes": {
            "kandji": "May require approval",
            "landscape": "Check with IT"
        }
    }
```

**Key:** Return OPTIONS, not commands. User/team chooses their method.

### Layer 3: Personal Installation Config (Optional)

Users can optionally configure their preferred installation method:

```yaml
# ~/.config/platform-mcp/install-config.yaml (OPTIONAL)
personal:
  os: "macos"
  mdm: "kandji"
  preferred_install_method: "ansible-mac"
  ansible_mac_path: "~/personal/git/ansible-mac"  # Only if using ansible-mac
```

**Key:** This is OPTIONAL. If it doesn't exist, tools return generic guidance.

### Layer 4: Bootstrap Helper (New)

A simple script that helps users get started:

```bash
./bootstrap.sh

# Detects:
# - OS (uname)
# - Existing dependencies
# - Suggests installation method
# - Optionally creates install-config.yaml
```

**Key:** This is a HELPER, not required. Advanced users can skip it.

## Decision Matrix

| Scenario | Detection | Guidance | Config |
|----------|-----------|----------|--------|
| tsh not installed | ❌ Not found | "Install via: brew/apt/manual" | Optional: preferred method |
| tsh installed (old) | ✅ v16.4.8 | "Consider upgrading to v17.7.1" | Optional: upgrade command |
| tsh installed (current) | ✅ v17.7.1 | "All good!" | N/A |

## Changes Required

### Remove Hardcoded Paths

**Files to change:**
- `src/layers/platform.py` - Remove `ANSIBLE_MAC_PATH`
- Tool responses - Remove `ansible_command` fields
- Documentation - Remove ansible-mac as only option

**Replace with:**
```python
# Before
"ansible_command": "ansible-playbook ~/personal/git/ansible-mac/playbooks/teleport.yml"

# After
"install_guidance": {
    "recommended": get_recommended_install_method(os_type),
    "alternatives": get_alternative_methods(os_type),
    "documentation": "See docs/INSTALLATION-GUIDE.md"
}
```

### Add OS Detection

```python
# New utility function
def detect_os() -> str:
    """Detect operating system"""
    import platform
    system = platform.system().lower()
    
    if system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    else:
        return "unknown"
```

### Add MDM Detection (Optional)

```python
def detect_mdm() -> Optional[str]:
    """Detect if machine is MDM-managed (best effort)"""
    if detect_os() == "macos":
        # Check for Kandji
        if Path("/Library/Kandji").exists():
            return "kandji"
    elif detect_os() == "linux":
        # Check for Landscape
        if Path("/etc/landscape").exists():
            return "landscape"
    return None
```

**Key:** This is informational only. Doesn't change functionality.

## New Documentation Structure

```
docs/
├── INSTALLATION-GUIDE.md          # NEW: OS-specific install paths
│   ├── Prerequisites
│   ├── macOS Installation
│   │   ├── Via Homebrew (recommended)
│   │   ├── Via ansible-mac (advanced)
│   │   └── Manual installation
│   ├── Linux Installation
│   │   ├── Via apt (recommended)
│   │   └── Manual installation
│   └── Verification
│
├── INSTALLATION-SYSTEM-DESIGN.md  # NEW: This document
│
├── MDM-CONSIDERATIONS.md          # NEW: Kandji, Landscape notes
│   ├── Kandji (macOS)
│   └── Landscape (Linux/Ubuntu)
│
└── FORKING-GUIDE.md               # EXISTING: Updated to reference new install docs
```

## Migration Path

### Phase 1: Decouple (No Breaking Changes)

1. Add OS detection utilities
2. Update tools to return both old AND new format:
   ```python
   {
       "ansible_command": "...",  # Deprecated but still present
       "install_guidance": {...}  # New format
   }
   ```
3. Update documentation to show multiple options
4. No code removal yet (backward compatible)

### Phase 2: Documentation

1. Create `INSTALLATION-GUIDE.md` with OS-specific paths
2. Create `MDM-CONSIDERATIONS.md` with Kandji/Landscape notes
3. Update `README.md` to not recommend ansible-mac as only option
4. Update `TEAM-ONBOARDING.md` to reference new install guide

### Phase 3: Cleanup (Breaking Change)

1. Remove `ANSIBLE_MAC_PATH` from platform layer
2. Remove `ansible_command` from tool responses
3. Remove ansible-mac references from error messages
4. Mark as breaking change in release notes

### Phase 4: Enhanced Bootstrap

1. Create `bootstrap.sh` helper script
2. Add optional `install-config.yaml` support
3. Create installation test suite

## Non-Goals

**What this design explicitly does NOT do:**

1. **Install dependencies automatically** - Users install their own way
2. **Package management** - Not an alternative to brew/apt/ansible
3. **MDM integration** - Just awareness, not automation
4. **Cross-platform abstraction** - Tools are still OS-specific where needed
5. **Installation enforcement** - Users can ignore guidance

## Success Criteria

### Phase 1 Complete When:
- ✅ OS detection working
- ✅ Tools return generic guidance (alongside old format)
- ✅ No breaking changes to existing users
- ✅ Tests pass on macOS and Linux

### Phase 2 Complete When:
- ✅ Documentation covers macOS, Linux, manual paths
- ✅ MDM considerations documented
- ✅ New team can onboard without ansible-mac

### Phase 3 Complete When:
- ✅ ansible-mac references removed
- ✅ Installation method is user choice, not hardcoded
- ✅ All tests updated
- ✅ Migration guide for existing users

### Phase 4 Complete When:
- ✅ Bootstrap script working
- ✅ Optional config support
- ✅ Installation tests on CI

## Open Questions

1. **Should we support Windows?** (Teleport works on Windows)
   - Decision: Start with macOS/Linux, Windows later if needed

2. **Should bootstrap.sh be interactive or generate config?**
   - Decision: Interactive with option to save config

3. **Should install-config.yaml be in repo or ~/.config/?**
   - Decision: `~/.config/platform-mcp/` (per-user, not per-repo)

4. **Should we provide Docker image as alternative?**
   - Decision: Future consideration, not in initial roadmap

5. **How do we handle multiple MCP servers on one machine?**
   - Decision: Each MCP server has its own config

## Testing Strategy

### Unit Tests
- OS detection
- Dependency checking
- Guidance generation

### Integration Tests
- Run on macOS CI (GitHub Actions)
- Run on Linux CI (GitHub Actions)
- Test with/without dependencies installed

### Manual Tests
- Fresh macOS machine (no ansible-mac)
- Fresh Linux machine
- Machine with Kandji
- Machine with Landscape

## Related Documents

- `ROADMAP.md` - Overall project roadmap
- `FORKING-GUIDE.md` - How teams fork this server
- `TEAM-ONBOARDING.md` - How teams adopt this server
- `DESIGN-PRINCIPLES.md` - Core architectural principles

## Conclusion

**Core Insight:** Installation is a bootstrap problem, not a runtime problem. The MCP server should be agnostic about HOW dependencies got installed, only THAT they are installed.

**Architectural Benefit:** Loose coupling means:
- Teams can use their preferred installation method
- OS support can be added independently
- MDM changes don't affect MCP server
- New installation methods don't require code changes

**Migration Benefit:** Existing setups continue working during transition.