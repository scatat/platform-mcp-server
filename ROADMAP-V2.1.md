# Platform MCP Server - Roadmap V2.1

## Overview

This roadmap covers the next phase of development: **Decoupling Installation from Runtime**.

**Current State (V2.0):**
- ✅ 3-layer architecture implemented
- ✅ Multi-team support ready
- ❌ ansible-mac hardcoded in multiple places
- ❌ macOS-only installation instructions
- ❌ Tight coupling between installation method and tool functionality

**Target State (V2.1):**
- Installation method is user choice, not hardcoded
- Works on macOS, Linux, and potentially Windows
- MDM-aware (Kandji, Landscape)
- Loose coupling: MCP server doesn't care HOW dependencies got installed

## Problem Statement

The MCP server currently assumes:
1. macOS with ansible-mac
2. Specific hardcoded paths (`~/personal/git/ansible-mac`)
3. Ansible as the only installation method

**Why This Matters:**
- Blocks adoption by non-Mac Wise teams (Compute, Connect, CI, CD)
- Blocks adoption by teams that don't use Ansible
- Makes forking harder (need to change hardcoded paths)
- Violates loose coupling principle

## Design Principles for V2.1

1. **Separation of Concerns**: Installation ≠ Runtime
2. **Configuration Over Convention**: User choice, not hardcoded
3. **Detect, Don't Prescribe**: Check what's installed, suggest options
4. **Backward Compatible**: Existing setups keep working
5. **OS Agnostic**: Works on macOS, Linux, Windows

## Migration Phases

### Phase 1: Decouple (Backward Compatible)

**Goal:** Remove hardcoded installation paths without breaking existing users

**Tasks:**
- [ ] Add OS detection utility (`detect_os()`)
- [ ] Add MDM detection utility (`detect_mdm()`) - informational only
- [ ] Update platform layer tools to return both old and new format:
  - Keep `ansible_command` (deprecated)
  - Add `install_guidance` (new)
- [ ] Create installation guidance generator (`get_install_guidance()`)
- [ ] Add tests for OS detection on macOS and Linux
- [ ] Add deprecation warnings for `ansible_command` field

**Success Criteria:**
- ✅ Tools work on macOS and Linux
- ✅ Existing users see no breaking changes
- ✅ New users see OS-appropriate guidance
- ✅ Tests pass on both macOS and Linux CI

**Estimated Effort:** 2-3 hours

### Phase 2: Documentation

**Goal:** Provide clear installation paths for different OS/methods

**Tasks:**
- [ ] Create `docs/INSTALLATION-GUIDE.md`
  - Prerequisites
  - macOS installation (brew, ansible-mac, manual)
  - Linux installation (apt, manual)
  - Verification steps
- [ ] Create `docs/MDM-CONSIDERATIONS.md`
  - Kandji (macOS) notes
  - Landscape (Linux/Ubuntu) notes
  - Permission/approval workflows
- [ ] Update `README.md`
  - Remove ansible-mac as "recommended" method
  - Show it as ONE option among many
  - Link to new installation guide
- [ ] Update `docs/TEAM-ONBOARDING.md`
  - Reference new installation guide
  - Show examples for different teams/OS
- [ ] Update `docs/FORKING-GUIDE.md`
  - Note that installation is decoupled
  - Teams can use their preferred method

**Success Criteria:**
- ✅ Non-Mac users can follow installation steps
- ✅ Teams understand their installation options
- ✅ MDM constraints are documented
- ✅ No assumption of specific installation method

**Estimated Effort:** 2-3 hours

### Phase 3: Cleanup (Breaking Change)

**Goal:** Remove deprecated patterns and hardcoded paths

**Tasks:**
- [ ] Remove `ANSIBLE_MAC_PATH` constant from `src/layers/platform.py`
- [ ] Remove `ansible_command` from all tool return values
- [ ] Remove ansible-mac references from error messages
- [ ] Update all tests to use new format
- [ ] Create migration guide for existing users
- [ ] Update CHANGELOG with breaking changes
- [ ] Bump version to V2.1.0

**Success Criteria:**
- ✅ No hardcoded installation paths in code
- ✅ Tools return only generic guidance
- ✅ All tests updated
- ✅ Existing users have migration path

**Estimated Effort:** 2-3 hours

**Breaking Changes:**
- `ansible_command` field removed from tool responses
- Tools no longer return specific ansible-mac commands
- Users must configure their own installation method

**Migration Path for Existing Users:**
1. Update to intermediate version (Phase 1 complete)
2. Test that both old and new formats work
3. Update any automation that depends on `ansible_command`
4. Upgrade to V2.1.0

### Phase 4: Enhanced Bootstrap (Optional/Future)

**Goal:** Make initial setup easier with helper script

**Tasks:**
- [ ] Create `bootstrap.sh` helper script
  - Detect OS
  - Detect existing dependencies
  - Suggest installation method
  - Optionally create `~/.config/platform-mcp/install-config.yaml`
- [ ] Add optional personal installation config support
  - User can specify preferred install method
  - Config is per-user, not per-repo
  - Completely optional
- [ ] Create installation test suite
  - Test on fresh macOS machine
  - Test on fresh Linux machine
  - Test with/without dependencies

**Success Criteria:**
- ✅ `bootstrap.sh` guides new users through setup
- ✅ Optional config reduces repeated guidance
- ✅ Installation tests run in CI

**Estimated Effort:** 3-4 hours

**Note:** This phase is optional. Core functionality works without it.

## Dependency Tree

```
Phase 1 (Decouple)
    ↓
Phase 2 (Documentation) ← Can start in parallel with Phase 1
    ↓
Phase 3 (Cleanup) ← Requires Phase 1 complete
    ↓
Phase 4 (Bootstrap) ← Optional, requires Phase 3 complete
```

**Critical Path:** Phase 1 → Phase 3 → Phase 4

**Parallel Work:** Phase 2 can start while Phase 1 is in progress

## Files to Change

### Code Changes

**Phase 1:**
- `src/layers/platform.py` - Add OS detection, update tool responses
- `platform_mcp.py` - No changes (decoupled from installation)
- `src/layers/team.py` - No changes (uses platform primitives)
- `src/layers/personal.py` - No changes (tool creation, not installation)

**Phase 3:**
- `src/layers/platform.py` - Remove `ANSIBLE_MAC_PATH`, remove deprecated fields
- All test files - Update assertions for new response format

### Documentation Changes

**Phase 2:**
- `docs/INSTALLATION-GUIDE.md` (new)
- `docs/MDM-CONSIDERATIONS.md` (new)
- `README.md` (update)
- `docs/TEAM-ONBOARDING.md` (update)
- `docs/FORKING-GUIDE.md` (update)

**Phase 3:**
- `CHANGELOG.md` (new entry for V2.1.0)
- `README.md` (remove old installation references)

### New Files

**Phase 4:**
- `bootstrap.sh` (new)
- Example: `~/.config/platform-mcp/install-config.yaml` (optional, per-user)

## Testing Strategy

### Phase 1 Tests

```python
def test_os_detection():
    """Test OS detection on different platforms"""
    assert detect_os() in ["macos", "linux", "windows", "unknown"]

def test_install_guidance_macos():
    """Test guidance returns brew for macOS"""
    guidance = get_install_guidance("tsh", os_type="macos")
    assert "brew install" in guidance["methods"]["recommended"]

def test_install_guidance_linux():
    """Test guidance returns apt for Linux"""
    guidance = get_install_guidance("tsh", os_type="linux")
    assert "apt install" in guidance["methods"]["recommended"]

def test_backward_compatibility():
    """Test tools still return ansible_command (deprecated)"""
    result = check_tsh_installed()
    assert "ansible_command" in result  # Deprecated but present
    assert "install_guidance" in result  # New format
```

### Phase 3 Tests

```python
def test_no_hardcoded_paths():
    """Ensure no hardcoded ansible-mac paths"""
    # Scan source files for hardcoded paths
    # Fail if found

def test_new_response_format():
    """Test tools use new format only"""
    result = check_tsh_installed()
    assert "install_guidance" in result
    assert "ansible_command" not in result  # Removed
```

## Success Metrics

### V2.1 Complete When:

1. **Loose Coupling**
   - ✅ No hardcoded installation paths in code
   - ✅ Installation method is user/team choice
   - ✅ MCP server works regardless of how dependencies installed

2. **Multi-OS Support**
   - ✅ Works on macOS (Intel and Apple Silicon)
   - ✅ Works on Linux (Ubuntu/Debian)
   - ✅ Documentation for both OS

3. **Multi-Team Ready**
   - ✅ Wise teams on different OS can adopt
   - ✅ Teams can use their preferred install method
   - ✅ MDM constraints documented

4. **Backward Compatible Migration**
   - ✅ Existing users have clear migration path
   - ✅ Breaking changes documented
   - ✅ Version bump follows semver

## Non-Goals for V2.1

**Explicitly NOT doing:**
1. Automatic dependency installation
2. Package manager abstraction
3. MDM integration/automation
4. Windows support (future consideration)
5. Docker/container images (future consideration)

## Open Questions

1. **Should we support Windows?**
   - Teleport works on Windows
   - Defer to future if demand exists

2. **Should install-config.yaml be required?**
   - No - completely optional
   - Only for users who want custom guidance

3. **How do we test on Linux in CI?**
   - GitHub Actions supports Ubuntu runners
   - Add Linux test job to CI workflow

4. **What about teams that use Terraform for laptop setup?**
   - Same principle: decoupled from MCP server
   - They install dependencies their way

5. **Should we provide example configs for common setups?**
   - Yes - in `docs/INSTALLATION-GUIDE.md`
   - Examples: brew, apt, ansible-mac, manual

## Timeline Estimate

**Fast Track (Minimal):**
- Phase 1 + 2: 1-2 sessions
- Phase 3: 1 session
- Total: 2-3 sessions, ~6-9 hours

**Complete (With Bootstrap):**
- Phase 1 + 2: 1-2 sessions
- Phase 3: 1 session
- Phase 4: 1-2 sessions
- Total: 3-5 sessions, ~10-15 hours

## Related Documents

- `docs/INSTALLATION-SYSTEM-DESIGN.md` - Detailed architecture design
- `ROADMAP.md` - V1.0 → V2.0 roadmap (completed)
- `docs/DESIGN-PRINCIPLES.md` - Core architectural principles
- `docs/FORKING-GUIDE.md` - How teams fork this server
- `docs/TEAM-ONBOARDING.md` - How teams adopt this server

## Conclusion

V2.1 focuses on **loose coupling** between installation and runtime. This enables:
- Multi-OS support (macOS, Linux)
- Multi-team adoption (different install preferences)
- Future flexibility (new install methods don't require code changes)

The core insight: **The MCP server shouldn't care HOW dependencies got installed, only THAT they are installed.**