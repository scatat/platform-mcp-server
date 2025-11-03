# Platform MCP Server - Roadmap V2.1

## Overview

This roadmap covers the next phase of development focused on three major areas:
1. **Decoupling Installation from Runtime** - OS-agnostic installation
2. **GitHub Operations** - CLI-based GitHub workflows
3. **AWS Operations** - SSO-based AWS management with tagging enforcement
4. **Policy as Configuration** - Template-based rule system

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

1. **Separation of Concerns**: Installation ≠ Runtime, Logic ≠ Data
2. **Configuration Over Convention**: User choice, not hardcoded
3. **Detect, Don't Prescribe**: Check what's installed, suggest options
4. **Backward Compatible**: Existing setups keep working
5. **OS Agnostic**: Works on macOS, Linux, Windows
6. **CLI Over API**: Use CLI tools with separate auth (gh, aws, tsh pattern)
7. **Policy as Configuration**: Rules in YAML, logic in code

## Feature Tracks

V2.1 has four parallel feature tracks that can be developed independently:

**Track A: Installation Decoupling** (Phases 1-4)
**Track B: GitHub Operations** (Phases 5-6)
**Track C: AWS Operations** (Phases 7-8)
**Track D: Policy Templating** (Phase 9)

---

## Track A: Installation Decoupling

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

---

## Track B: GitHub Operations

### Phase 5: GitHub CLI Integration

**Goal:** Streamline commit → push → PR workflow using `gh` CLI

**Why gh CLI Instead of GitHub MCP:**
- GitHub MCP requires PAT in config (security concern)
- `gh` CLI uses separate auth (`gh auth login`)
- More token efficient
- Follows existing pattern (like Teleport/Flux)

**Tools to Add (Platform Layer):**
- [ ] `check_gh_installed()` - Verify gh CLI (like check_tsh_installed)
- [ ] `check_gh_auth()` - Verify gh authentication status
- [ ] `create_pr()` - Create PR with auto-assign and labels
- [ ] `list_prs()` - List PRs for current repo
- [ ] `get_pr_status()` - Get PR details + CI checks
- [ ] `list_actions_runs()` - View GitHub Actions status
- [ ] `get_actions_run()` - Details of specific Actions run

**PR Label System:**
Standard labels for all PRs:
- `change:standard` (default, 99% of cases)
- `change:impactful`
- `change:emergency`

**Success Criteria:**
- ✅ Can create PR with one command
- ✅ Auto-assigns to current user
- ✅ Auto-labels with change type
- ✅ Can view Actions status without browser
- ✅ No PAT required (uses gh auth)

**Estimated Effort:** 3-4 hours

### Phase 6: GitHub Workflow Automation

**Goal:** End-to-end git workflows

**Tools:**
- [ ] `commit_push_pr()` - Commit, push, create PR in one operation
- [ ] `update_pr()` - Update PR title, description, labels
- [ ] `merge_pr()` - Merge PR with options (squash, merge, rebase)
- [ ] `get_repo_info()` - Get current repo details
- [ ] `check_branch_protection()` - Verify branch protection rules

**Workflow Example:**
```python
# One command to commit, push, and create PR
result = commit_push_pr(
    message="Fix bug in auth",
    change_type="standard"  # Auto-labels with change:standard
)
# Returns PR URL and Actions status
```

**Success Criteria:**
- ✅ Full git workflow without leaving AI chat
- ✅ Safe defaults (change:standard)
- ✅ Can override when needed (change:impactful)

**Estimated Effort:** 2-3 hours

---

## Track C: AWS Operations

### Phase 7: AWS SSO and Tagging

**Goal:** AWS operations with SSO authentication and mandatory tagging

**Why This Matters:**
- 150+ AWS accounts at Wise
- All use SSO (not IAM credentials)
- Mandatory tagging for security/compliance
- Account naming follows pattern: `{domain}-{environment}`

**Account Naming Pattern:**
```
fps-uk-production     → domain: fps-uk,     env: production
npp-aus-staging       → domain: npp-aus,    env: staging
pi-hsm-staging        → domain: pi-hsm,     env: staging
k8s-main-sandbox      → domain: main,       env: sandbox
o11y-shared-service   → domain: o11y,       env: shared-service
```

**Required Tags:**
```python
{
    "wise:security-domain": "fps-uk",           # From account name
    "wise:security-environment": "production",  # From account name
    "wise:maintainer": "platform-integrations", # Team-specific
    "wise:owner": "platform-integrations",      # Team-specific
    "wise:managed-by": "terraform"              # Default
}
```

**Tools to Add (Platform Layer):**
- [ ] `check_aws_installed()` - Verify AWS CLI
- [ ] `check_aws_sso_auth()` - Check SSO authentication status
- [ ] `aws_sso_login()` - Login to AWS SSO profile
- [ ] `list_aws_profiles()` - List available SSO profiles
- [ ] `get_current_aws_account()` - Get current account info
- [ ] `parse_account_tags()` - Parse domain/env from account name
- [ ] `audit_resource_tags()` - Check resources for missing tags
- [ ] `plan_tag_updates()` - Generate tag update plan (dry-run)
- [ ] `apply_tag_updates()` - Apply tags (with confirmation)

**Safety Features:**
- **Dry-run first**: Always show plan before applying
- **Rebuild warnings**: Warn if tagging will trigger resource rebuilds
- **Confirmation required**: Never auto-apply destructive changes
- **ASG special handling**: Warn that ASG tag changes may trigger instance replacement

**Success Criteria:**
- ✅ Can use any AWS SSO profile
- ✅ Auto-detect domain/env from account name
- ✅ Audit resources for missing tags
- ✅ Safe tag application with warnings
- ✅ Works with Terraform workflows

**Estimated Effort:** 4-5 hours

**Resources that may rebuild when tagged:**
- Auto Scaling Groups (ASGs) - May replace instances
- Launch Templates - Creates new version
- Some Lambda functions - May redeploy
- Need to research others

### Phase 8: AWS Resource Operations

**Goal:** Common AWS read/modify operations

**Tools to Add:**
- [ ] `list_ec2_instances()` - List EC2 instances with filters
- [ ] `get_ec2_status()` - Get instance status
- [ ] `list_s3_buckets()` - List S3 buckets
- [ ] `list_rds_instances()` - List RDS instances
- [ ] `get_resource_tags()` - Get tags for any resource
- [ ] `update_resource_tags()` - Update tags for resource

**Use Cases:**
- Query resources across accounts
- Audit tag compliance
- Support Terraform operations (via profile selection)
- Read-only operations (safe)
- Modify operations with safeguards

**Success Criteria:**
- ✅ Can query resources across 150+ accounts
- ✅ All operations use --profile flag
- ✅ Safe defaults (read-only preferred)
- ✅ Clear warnings for destructive ops

**Estimated Effort:** 3-4 hours

---

## Track D: Policy as Configuration

### Phase 9: Policy Templating System

**Goal:** Separate rule logic (code) from rule data (config)

**Problem:**
Current: Rules hardcoded in Python
- Hard to review
- Hard to audit
- Hard to customize per team
- Hard to spot issues

**Solution:**
Rule templates (logic) + Team data (config) → Enforcement

**Architecture:**

```
rules/                      # Rule templates (logic)
├── aws-tagging.yaml       # AWS tagging requirements
├── github-pr.yaml         # GitHub PR standards
└── design-validation.yaml # Tool design checklist

teams/                      # Team data (config)
├── platform-integrations.yaml
├── compute.yaml
└── connect.yaml

Platform evaluates: template + data → enforcement
```

**Example Rule Template:**
```yaml
# rules/aws-tagging.yaml
rule_id: aws_required_tags
description: All AWS resources must have security tags
applies_to:
  resource_types: [ec2, s3, rds, asg, lambda]
required_tags:
  - name: wise:security-domain
    source: account_name  # Parse from account
  - name: wise:security-environment
    source: account_name  # Parse from account
  - name: wise:maintainer
    source: team_config   # From team data
  - name: wise:owner
    source: team_config   # From team data
  - name: wise:managed-by
    default: terraform
severity: error
rebuild_risk:
  - asg: "May trigger instance replacement"
  - launch_template: "Creates new version"
```

**Example Team Data:**
```yaml
# teams/platform-integrations.yaml
team_name: platform-integrations
aws_accounts:
  - fps-uk-production
  - fps-uk-staging
  - npp-aus-production
  - npp-aus-staging
  - pi-hsm-staging
  - pi-shared-services
default_tags:
  wise:maintainer: platform-integrations
  wise:owner: platform-integrations
  wise:managed-by: terraform
github_settings:
  default_pr_label: change:standard
```

**Tools to Add:**
- [ ] `load_rule_template()` - Load and parse rule template
- [ ] `load_team_config()` - Load team configuration
- [ ] `evaluate_policy()` - Evaluate template + config → result
- [ ] `list_policy_violations()` - Check for violations
- [ ] `validate_rule_template()` - Validate template syntax

**Benefits:**
- **Human readable**: Review rules by reading YAML
- **Easy to audit**: Version control for rules and data
- **Team customization**: Teams override defaults
- **Reusable**: Same template, different data
- **Testable**: Mock data for testing

**Success Criteria:**
- ✅ Rules are YAML files (not Python code)
- ✅ Team data is separate from logic
- ✅ Easy to spot issues by reading config
- ✅ Can add new rules without code changes
- ✅ Backward compatible with existing validation

**Estimated Effort:** 5-6 hours

**Applies To:**
- AWS tagging enforcement
- GitHub PR standards
- Design validation (already uses design-checklist.yaml!)
- Any policy enforcement

---

## Dependency Tree

### Track A (Installation):
```
Phase 1 (Decouple)
    ↓
Phase 2 (Documentation) ← Can start in parallel with Phase 1
    ↓
Phase 3 (Cleanup) ← Requires Phase 1 complete
    ↓
Phase 4 (Bootstrap) ← Optional, requires Phase 3 complete
```

### Track B (GitHub):
```
Phase 5 (GitHub CLI) → Phase 6 (Workflows)
```
Independent of other tracks

### Track C (AWS):
```
Phase 7 (SSO + Tagging) → Phase 8 (Resource Ops)
```
Independent of other tracks

### Track D (Policy):
```
Phase 9 (Templating System)
```
Can start anytime, enhances Phase 7 if done after

**Parallel Work:**
- All tracks can be developed in parallel
- Track D enhances other tracks but not required
- Recommended order: A → B → C → D (but flexible)

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

#### Track A (Installation):
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

#### Track B (GitHub):
1. **Streamlined Workflow**
   - ✅ Can create PR with one command
   - ✅ Auto-assignment and labeling works
   - ✅ Can view Actions without browser

2. **Security**
   - ✅ No PAT required in config
   - ✅ Uses gh auth separately
   - ✅ Follows CLI pattern

#### Track C (AWS):
1. **SSO Support**
   - ✅ Works with AWS SSO (not IAM credentials)
   - ✅ Can use any of 150+ profiles
   - ✅ SSO login workflow

2. **Tagging Enforcement**
   - ✅ Can audit missing tags
   - ✅ Can apply tags safely
   - ✅ Warns about rebuild risks
   - ✅ Auto-detects domain/env from account name

3. **Safety**
   - ✅ Dry-run mode works
   - ✅ Confirmation required for destructive ops
   - ✅ Clear warnings for ASGs and other risky resources

#### Track D (Policy):
1. **Separation**
   - ✅ Rules in YAML files
   - ✅ Team data in separate config
   - ✅ Logic in code (template engine)

2. **Usability**
   - ✅ Human-readable rule files
   - ✅ Easy to audit
   - ✅ Teams can customize

## Non-Goals for V2.1

**Explicitly NOT doing:**
1. Automatic dependency installation
2. Package manager abstraction
3. MDM integration/automation
4. Windows support (future consideration)
5. Docker/container images (future consideration)
6. GitHub API usage (using CLI instead)
7. AWS API direct usage (using CLI instead)
8. Creating AWS resources (read/modify only)
9. Automatic tag application (always requires confirmation)

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

**Track A (Installation) - Minimal:**
- Phase 1 + 2: 1-2 sessions (~6-9 hours)
- Phase 3: 1 session (~2-3 hours)
- Total: 2-3 sessions, ~6-9 hours

**Track A (Installation) - Complete:**
- Phase 1-4: 3-5 sessions (~10-15 hours)

**Track B (GitHub):**
- Phase 5-6: 2-3 sessions (~5-7 hours)

**Track C (AWS):**
- Phase 7-8: 3-4 sessions (~7-9 hours)

**Track D (Policy):**
- Phase 9: 2-3 sessions (~5-6 hours)

**All Tracks Complete:**
- Total: 10-15 sessions, ~27-37 hours

**Recommended Sequence:**
1. Track A (Installation) - Unblocks multi-team adoption
2. Track B (GitHub) - High value, low complexity
3. Track C (AWS) - High value, higher complexity
4. Track D (Policy) - Enhances others, do last

## Related Documents

- `docs/INSTALLATION-SYSTEM-DESIGN.md` - Detailed architecture design
- `ROADMAP.md` - V1.0 → V2.0 roadmap (completed)
- `docs/DESIGN-PRINCIPLES.md` - Core architectural principles
- `docs/FORKING-GUIDE.md` - How teams fork this server
- `docs/TEAM-ONBOARDING.md` - How teams adopt this server

## Conclusion

V2.1 focuses on four key areas:

1. **Loose Coupling** - Installation and runtime are separate
2. **CLI-First** - Use CLI tools (gh, aws) with separate auth (no PATs/credentials in config)
3. **Safety First** - Dry-run, warnings, confirmations for destructive operations
4. **Policy as Configuration** - Separate rule logic from team data

**Core Insights:**
- The MCP server shouldn't care HOW dependencies got installed, only THAT they are installed
- Use CLI tools over APIs - simpler, more secure, token efficient
- Rules should be readable YAML, not hidden in code
- Always plan before applying, especially for AWS operations

**Value Proposition:**
- Track A enables multi-team, multi-OS adoption
- Track B streamlines daily git workflows
- Track C enables safe AWS operations at scale
- Track D makes rules auditable and maintainable