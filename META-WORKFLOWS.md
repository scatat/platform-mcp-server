# Meta-Workflows: Process Bank for Platform Engineering

**Purpose:** A "memory bank" of commonly-used processes and workflows for AI-assisted platform engineering. This allows you to invoke complex multi-step processes with simple natural language triggers.

**Date Created:** 2024-11-02  
**Date Updated:** 2024-01-07 (Added MW-008, Organized by category, Added efficiency enforcement)  
**Status:** Living Document

**Organization:** Workflows are now categorized by scope:
- **Universal**: Core MCP development (any team can use)
- **Team**: Our infrastructure-specific (Flux, K8s, Teleport)
- **Personal**: Individual setup (ansible-mac)
- See `resources/workflows/README.md` for details

## 🔍 Auto-Discovery (New!)

As of V1c, meta-workflows are **automatically discoverable** via the MCP server:

- **Tool: `list_meta_workflows()`** - Returns structured list of all workflows with trigger phrases
- **Resource: `workflow://meta-workflows`** - Exposes this entire document as readable context

**What This Means:**
- The AI can now discover workflows without being told they exist
- No more "chicken-and-egg" problem in new sessions
- The system is self-documenting

## ⚡ Efficiency Enforcement (New!)

As of V1d, **efficiency analysis is now enforced programmatically**:

- **Tool: `analyze_critical_path()`** - Analyzes task dependencies and returns optimal work order + analysis token
- **Tool: `make_roadmap_decision()`** - Requires analysis token, enforces that decisions are based on critical path analysis

**What This Means:**
- AI cannot make roadmap decisions without first analyzing efficiency
- Similar to design validation enforcement for tool creation
- Prevents "here are your options" responses without proper analysis
- Forces optimal task ordering based on dependencies

**How to Use:**
```
# AI can call this automatically to discover workflows
list_meta_workflows()

# Returns: List of 8 workflows with IDs, names, triggers, and status
# Example: MW-001, "Thread Ending Summary", "This thread is ending", "active"
```

---

## Table of Contents

1. [Meta-Workflow System Overview](#meta-workflow-system-overview)
2. [Workflow Registry](#workflow-registry)
3. [Creating New Meta-Workflows](#creating-new-meta-workflows)
4. [Session Management Workflows](#session-management-workflows)
5. [MCP Development Workflows](#mcp-development-workflows)
6. [Platform Operations Workflows](#platform-operations-workflows)

---

## Meta-Workflow System Overview

### What is a Meta-Workflow?

A **meta-workflow** is a documented, repeatable process that the AI can execute when you invoke it with a trigger phrase. It's like a "stored procedure" for AI assistance.

**Discovery:** The AI can discover available workflows by calling `list_meta_workflows()` - no manual prompting needed!

### Why Meta-Workflows?

1. **Consistency** - Same steps every time, no missed steps
2. **Efficiency** - Complex processes become single commands
3. **Memory** - AI doesn't need to remember, it follows the script
4. **Disambiguation** - Clear boundaries prevent workflow interference
5. **Onboarding** - New AI sessions can execute workflows immediately

### Meta-Workflow Structure

```yaml
workflow_name: "Short descriptive name"
trigger_phrases:
  - "Primary natural language trigger"
  - "Alternative trigger phrase"
scope: "What this workflow covers"
disambiguates_from: ["Other workflows it might be confused with"]
prerequisites: ["What must be true before starting"]
steps:
  - description: "Step 1"
    actions: ["Specific actions to take"]
    validation: "How to verify step completed"
  - description: "Step 2"
    ...
outputs:
  - "What artifacts/documents are produced"
success_criteria:
  - "How to know workflow completed successfully"
```

---

## Workflow Registry

**Organization**: Workflows are categorized by scope (see `resources/workflows/README.md`)
- **Universal**: Applicable to any MCP development, any team
- **Team**: Specific to our infrastructure (Flux, Kubernetes, Teleport)
- **Personal**: Individual developer setup (ansible-mac)

### Universal Workflows (Core MCP Development)

| ID | Name | Trigger | Status | Last Updated |
|----|------|---------|--------|--------------|
| MW-001 | Thread Ending Summary | "This thread is ending" | Active | 2024-11-02 |
| MW-002 | New MCP Tool Development | "Create new MCP tool" | Active | 2024-01-07 |
| MW-003 | MCP Tool Testing Suite | "Test MCP tools" | Active | 2024-11-02 |
| MW-005 | Create Meta-Workflow | "Create new meta-workflow" | Active | 2024-11-02 |
| MW-008 | Architectural Discovery & Correction | "That doesn't match my understanding" | Active | 2024-01-07 |
| MW-009 | Tool Enhancement/Modification | "Modify existing tool" / "Enhance tool" | Active | 2024-01-07 |

### Team Workflows (Infrastructure-Specific)

| ID | Name | Trigger | Status | Last Updated |
|----|------|---------|--------|--------------|
| MW-006 | Flux Debugging Session | "Debug Flux issues" | Draft | 2024-11-02 |

### Personal Workflows (Individual Setup)

| ID | Name | Trigger | Status | Last Updated |
|----|------|---------|--------|--------------|
| MW-004 | Deploy MCP Changes | "Deploy MCP changes" | Active | 2024-11-02 |

### Draft Workflows (Under Development)

| ID | Name | Trigger | Status | Last Updated |
|----|------|---------|--------|--------------|
| MW-007 | New Tool Category | "Create new tool category" | Draft | 2024-11-02 |

---

## Creating New Meta-Workflows

### MW-005: Create New Meta-Workflow

**Trigger Phrases:**
- "I want to create a new platform meta workflow"
- "Create new meta-workflow"
- "Add a new workflow to the registry"

**Scope:** Creating and documenting a new repeatable workflow

**Prerequisites:**
- User has a clear process in mind
- Process has been done at least once manually

**Steps:**

#### 1. Gather Requirements
**Actions:**
- Ask: "What is the workflow name?"
- Ask: "What natural language trigger phrases should invoke it?"
- Ask: "What is the scope/purpose of this workflow?"
- Ask: "What are the prerequisites before starting?"
- Ask: "What are the main steps involved?"
- Ask: "What outputs/artifacts should it produce?"

**Validation:** User has provided clear answers to all questions

#### 2. Check for Ambiguity
**Actions:**
- Review existing workflows in registry
- Identify any workflows with similar:
  - Trigger phrases
  - Scope/purpose
  - Steps or outcomes
- Ask: "I found similar workflow(s): [list]. How does your workflow differ?"
- Confirm: "Should this replace, extend, or coexist with [existing workflow]?"

**Validation:** No ambiguous overlaps, or overlaps are intentionally documented

#### 3. Document the Workflow
**Actions:**
- Assign next available MW-ID (e.g., MW-008)
- Create workflow documentation following structure
- Add disambiguation notes if needed
- Include examples of when to use vs. not use

**Validation:** Workflow is fully documented in META-WORKFLOWS.md

#### 4. Add to Registry
**Actions:**
- Add entry to Workflow Registry table
- Update Table of Contents if new category needed
- Cross-reference with related workflows

**Validation:** Registry updated, workflow discoverable

#### 5. Test the Workflow
**Actions:**
- AI simulates workflow execution (dry run)
- Identify any unclear steps or decision points
- Refine based on findings

**Validation:** Workflow can be executed unambiguously

**Outputs:**
- Updated META-WORKFLOWS.md with new workflow
- Registry entry created
- Disambiguation notes (if applicable)

**Success Criteria:**
- [ ] Workflow fully documented
- [ ] Registry updated
- [ ] No ambiguous overlaps
- [ ] Can be executed by AI in future sessions

---

## Session Management Workflows

### MW-001: Thread Ending Summary

**Trigger Phrases:**
- "This thread is ending"
- "Create session summary"
- "We're running out of tokens"
- "Time to wrap up this session"

**Scope:** Creating comprehensive session summary for future continuation

**Disambiguates From:** 
- MW-002 (focuses on tool development, not session state)
- Regular status updates (which are less comprehensive)

**Prerequisites:**
- Significant work has been done in this session
- Changes have been committed to git
- Token count is getting high (>800k used)

**Steps:**

#### 1. Assess Session State
**Actions:**
- Review what was accomplished this session
- Identify what's complete vs. in-progress
- Note any unresolved issues or blockers
- Check git commit history for changes made

**Validation:** Clear understanding of session achievements

#### 2. Extract Persistent Documentation from Ephemeral State
**Actions:**
- Review working notes in `.ephemeral/sessions/` (if any)
- Extract valuable information:
  - What was accomplished? → Summary
  - What decisions were made? → Document
  - What was learned? → Capture
- Create `docs/sessions/VXx/FINAL-SUMMARY.md` (where VXx = version/date)
- Include sections:
  - Executive Summary
  - System Architecture (if changed)
  - Implemented Tools/Features (with details)
  - Key Configuration Details
  - Testing Results
  - Known Issues & Gotchas
  - What's Next / Future Work
  - Quick Reference Commands
  - Important Notes for AI Continuation
- Use previous session summaries in `docs/sessions/` as template
- Update metrics (LOC, tool count, coverage)

**Validation:** Summary document is comprehensive and self-contained

#### 3. Document Testing Status
**Actions:**
- List what was tested and results
- Document what still needs testing
- Provide exact test commands for next session
- Note any test failures and workarounds

**Validation:** Future AI can resume testing immediately

#### 4. Create Next Session Checklist
**Actions:**
- List first tasks for next session
- Provide exact commands to run
- Set context for what to build next
- Estimate time/complexity for next work

**Validation:** Clear starting point defined

#### 5. Final Git State Check
**Actions:**
- Verify all changes committed
- Confirm git push completed
- Check no uncommitted changes remain
- Document any work-in-progress branches

**Validation:** Git state is clean and synced

#### 6. Create Continuation Instructions
**Actions:**
- State exact file to read first
- List key facts AI must remember
- Provide troubleshooting checklist
- Include workflow names for common operations

**Validation:** Next AI session can start immediately without questions

**Outputs:**
- `docs/sessions/VXx/FINAL-SUMMARY.md` (comprehensive state document)
- `.ephemeral/sessions/` cleaned up or archived
- Updated README (if needed)
- Clear continuation instructions

**Success Criteria:**
- [ ] Summary document created/updated
- [ ] All work committed and pushed
- [ ] Testing status documented
- [ ] Next steps clearly defined
- [ ] Future AI can resume seamlessly

**Example Execution:**
```
User: "This thread is ending"
AI: "I'll create the session summary. Let me:
     1. Review ephemeral working notes in .ephemeral/sessions/...
     2. Extract valuable information...
     3. Create docs/sessions/V1d/FINAL-SUMMARY.md...
     4. Document testing status...
     5. Define next steps...
     Done! Summary created with 481 lines of documentation.
     Ephemeral files archived."
```

**Related Files:**
- `.ephemeral/README.md` - Explains transient state pattern
- `docs/sessions/README.md` - Explains persistent session documentation
- `ROADMAP.md` - State management strategy

---

## MCP Development Workflows

### MW-002: New MCP Tool Development

**Trigger Phrases:**
- "Create new MCP tool"
- "Add a new tool to the MCP server"
- "Build a new platform tool"

**Scope:** Full lifecycle of adding a single MCP tool

**Disambiguates From:**
- MW-007 (which creates entire tool *categories*, not single tools)
- MW-004 (which deploys existing changes, doesn't create new tools)

**Prerequisites:**
- Clear understanding of what tool should do
- Know which existing tools/primitives it will use
- Have test environment ready

**Steps:**

#### 1. Requirements Gathering
**Actions:**
- Ask: "What should this tool do?"
- Ask: "What parameters does it need?"
- Ask: "What does it return?"
- Ask: "Is this read-only or does it modify state?"
- Ask: "Which existing tools/primitives will it use?"

**Validation:** Clear specification of tool behavior

#### 2. ⚠️ MANDATORY Design Validation
**⚠️ CRITICAL STEP - CANNOT BE SKIPPED ⚠️**

**Why This Matters:**
This step prevents technical debt by validating design against established principles BEFORE implementation. Catching issues early is 10x faster than fixing them later.

**⚠️ ENFORCEMENT MECHANISM (NEW - 2025-01-07):**
Design validation is now **programmatically enforced** via MCP tools. You MUST call `propose_tool_design()` before implementation.

**Actions:**
1. **Call the validation tool:**
   ```python
   result = propose_tool_design(
       tool_name="your_tool_name",
       purpose="One sentence description",
       layer="platform|team|personal",
       dependencies=["list", "of", "dependencies"],
       requires_system_state_change=False,  # True if it modifies system state
       implementation_approach="Brief description of how it will work"
   )
   ```

2. **Review validation results:**
   - If `result["valid"] == True`: Save the token and proceed to implementation
   - If `result["valid"] == False`: Fix all issues in `result["issues"]` and resubmit
   - Review warnings in `result["warnings"]` (non-blocking but important)

3. **Save validation token:**
   - Token: `result["token"]`
   - Include this token in your implementation commit message
   - Example: `feat: Add new_tool (validation: valid-abc123-xyz789)`

**What the validation checks:**

   - **Configuration vs Code:** Detects hardcoded infrastructure details
   - **Layer Placement:** Validates tool belongs in the correct layer
   - **Dependencies:** Checks for proper abstraction and composition
   - **Ansible-First Principle:** Enforces that system state changes use Ansible (not shell scripts)
   - **Red Flags:** Scans for anti-patterns (god tools, tight coupling, etc.)

4. **Manual checklist (for your understanding):**
   
   Read `resources/rules/design-checklist.yaml` to understand:
   - Configuration vs Code principles
   - Layer placement rules
   - Dependency management patterns
   - Testing criteria
   - Red flag patterns to avoid

**Validation Criteria:**
- ✅ `propose_tool_design()` returns `valid: true`
- ✅ NO blocking issues in `result["issues"]`
- ✅ Validation token saved for commit message
- ✅ Warnings reviewed and acknowledged

**If validation fails:**
- ⚠️ STOP - Do not proceed to implementation
- 🔧 Fix ALL issues listed in `result["issues"]`
- ♻️ Call `propose_tool_design()` again with fixes
- ✅ Only proceed when `valid: true`

**Output Required:**
- Validation token from successful `propose_tool_design()` call
- Proposal saved in `.ephemeral/tool-proposals/` (automatic)

**Example Success:**
```
result = propose_tool_design(
    tool_name="list_flux_kustomizations",
    purpose="List all Flux Kustomizations in a cluster",
    layer="team",
    dependencies=["run_remote_command", "kubectl"],
    requires_system_state_change=False,
    implementation_approach="Uses run_remote_command to execute 'kubectl get kustomizations -A -o json'"
)

# result["valid"] == True
# result["token"] == "valid-abc123-xyz789..."
# result["proposal_path"] == ".ephemeral/tool-proposals/abc123_list_flux_kustomizations.json"

# ✅ Proceed to implementation
```

**Example Failure:**
```
result = propose_tool_design(
    tool_name="install_packages",
    purpose="Install packages on servers",
    layer="platform",
    dependencies=["bash"],
    requires_system_state_change=True,
    implementation_approach="Creates install.sh script and runs it on staging and production"
)

# result["valid"] == False
# result["issues"] == [
#     "❌ Ansible-first principle violation: System state changes must use Ansible",
#     "⚠️ Hardcoded configuration detected: 'staging', 'production'"
# ]

# ⚠️ STOP - Fix issues and resubmit
```

**Audit Trail:**
All validated proposals are stored in `.ephemeral/tool-proposals/` with:
- Proposal ID and timestamp
- Full design details
- Validation results
- Cryptographic token

This creates accountability and makes it easy to review what was approved vs. what was implemented.

#### 3. Check for Redundancy
**Actions:**
- Review existing tools in platform_mcp.py
- Search for similar functionality
- Ask: "Tool X does something similar. Should we extend it instead?"
- Confirm: "This is a new tool, not a modification of existing"

**Validation:** No duplicate functionality

#### 4. Security Review
**Actions:**
- Identify all user inputs
- Determine if inputs go into commands
- Plan shlex.quote() usage
- Verify cluster name validation
- Check if sudo/privilege escalation needed
- Document security measures in docstring

**Validation:** Security requirements identified

#### 5. Implement Tool
**Actions:**
- Follow existing code patterns (see SESSION-SUMMARY)
- Use @mcp.tool() decorator
- Add comprehensive docstring with examples
- Implement input validation
- Use run_remote_command() or other primitives
- Return standard dict format: {success, message, ansible_command, ansible_steps, ...}
- Add inline comments explaining each step

**Validation:** Code follows established patterns

#### 6. Local Testing
**Actions:**
- Test in platform-mcp-server venv
- Test with valid inputs
- Test with invalid inputs
- Test error cases
- Verify return format matches spec

**Validation:** Tool works as expected locally

#### 7. Commit Changes
**Actions:**
- git add platform_mcp.py
- git commit with descriptive message
- git push

**Validation:** Changes in git history

#### 8. Deploy via Ansible
**Actions:**
- cd ~/personal/git/ansible-mac
- ansible-playbook playbooks/zed-mcp.yml
- Verify sync completed

**Validation:** Ansible reports success

#### 9. Integration Testing
**Actions:**
- Restart Zed Preview
- Test tool with natural language prompts
- Verify tool appears in MCP tool list
- Test with real cluster/node

**Validation:** Tool works in Zed Preview

#### 10. Update Documentation
**Actions:**
- Add tool to SESSION-SUMMARY tool list
- Update tool count metrics
- Add usage examples
- Update "What's Next" section if needed

**Validation:** Documentation reflects new tool

**Outputs:**
- New @mcp.tool() function in platform_mcp.py
- Git commit with changes
- Updated documentation
- Tested and working tool

**Success Criteria:**
- [ ] Requirements clearly documented
- [ ] Design validated against checklist (Step 2)
- [ ] No red flags present
- [ ] Layer placement justified
- [ ] Tool implemented with security measures
- [ ] Local tests pass
- [ ] Changes committed and deployed
- [ ] Works in Zed Preview
- [ ] Documentation updated

---

### MW-003: MCP Tool Testing Suite

**Trigger Phrases:**
- "Test MCP tools"
- "Run MCP test suite"
- "Verify MCP tools work"

**Scope:** Comprehensive testing of MCP tools

**Prerequisites:**
- MCP server code is up to date
- Have access to test clusters
- Logged into Teleport

**Steps:**

#### 1. Local Python Testing
**Actions:**
- cd platform-mcp-server
- source venv/bin/activate
- Run test files: test_teleport_v1b.py, test_teleport_v1c.py, etc.
- Capture any failures

**Validation:** Test scripts run without errors

#### 2. Integration Testing in Zed
**Actions:**
- Use natural language prompts for each tool
- Test with valid parameters
- Test edge cases
- Verify responses are helpful

**Validation:** All tools respond correctly in Zed

#### 3. Real-World Scenario Testing
**Actions:**
- Pick actual platform engineering task
- Use tools to accomplish it
- Verify workflow is smooth
- Note any usability issues

**Validation:** Tools solve real problems

#### 4. Document Test Results
**Actions:**
- Update SESSION-SUMMARY with test status
- Note any bugs found
- List tools that need improvement
- Update "Known Issues" section

**Validation:** Test results recorded

**Outputs:**
- Test execution results
- Bug list (if any)
- Updated documentation

---

### MW-004: Deploy MCP Changes

**Trigger Phrases:**
- "Deploy MCP changes"
- "Sync MCP server"
- "Update Zed with latest MCP code"

**Scope:** Deploy committed MCP changes to Zed Preview

**Prerequisites:**
- Changes committed to git
- Changes pushed to GitHub

**Steps:**

#### 1. Verify Git State
**Actions:**
- Check git status is clean
- Confirm changes are pushed
- Note commit hash

**Validation:** No uncommitted changes, push succeeded

#### 2. Run Ansible Sync
**Actions:**
- cd ~/personal/git/ansible-mac
- ansible-playbook playbooks/zed-mcp.yml
- Wait for completion
- Check for errors (ignore WhatsApp failure)

**Validation:** Ansible reports success

#### 3. Restart Zed Preview
**Actions:**
- Instruct user to restart Zed Preview
- Explain: ⌘-Shift-P → "Zed: Restart"

**Validation:** User confirms restart

#### 4. Verify Deployment
**Actions:**
- Test a tool to confirm new code is loaded
- Check MCP server version/state if applicable

**Validation:** New code is active

**Outputs:**
- MCP server updated in /Users/stephen.tan/src/mcp-servers/
- Zed Preview running latest code

---

### MW-007: Create New Tool Category

**Trigger Phrases:**
- "Create new tool category"
- "Start a new V1x category"
- "Build a new suite of tools"

**Scope:** Creating an entire category of related tools (like V1c)

**Disambiguates From:**
- MW-002 (single tool, not a category)

**Prerequisites:**
- Clear theme for tool category
- Multiple related tools identified
- Understand how tools relate to each other

**Steps:**

#### 1. Category Planning
**Actions:**
- Ask: "What is the category name? (e.g., V1d, V2a)"
- Ask: "What is the theme/purpose?"
- Ask: "What tools will be in this category?"
- Ask: "How do these tools relate to existing categories?"
- Create category scope document

**Validation:** Clear category definition

#### 2. Design Tool Interactions
**Actions:**
- Identify primitives needed
- Plan tool composition (which tools use which)
- Design common patterns for this category
- Document security considerations

**Validation:** Category architecture defined

#### 3. Implement Tools Iteratively
**Actions:**
- Use MW-002 for each tool
- Test each before moving to next
- Update documentation progressively

**Validation:** All category tools implemented

#### 4. Create Category Summary
**Actions:**
- Add category section to SESSION-SUMMARY
- Document architecture
- Provide usage examples
- Update metrics

**Validation:** Category fully documented

**Outputs:**
- New tool category code
- Category documentation
- Updated SESSION-SUMMARY

---

## Platform Operations Workflows

### MW-006: Flux Debugging Session (DRAFT)

**Trigger Phrases:**
- "Debug Flux issues"
- "Investigate Flux problems"
- "Troubleshoot GitOps deployment"

**Scope:** Systematic debugging of Flux reconciliation issues

**Steps:**

#### 1. Identify Problem Kustomization
#### 2. Check Kustomization Status
#### 3. Review Events
#### 4. Check Source Status
#### 5. Review Controller Logs
#### 6. Identify Root Cause
#### 7. Recommend Fix

*(This workflow is still being refined)*

---

### MW-008: Architectural Discovery & Correction

**Trigger Phrases:**
- "That doesn't match my understanding"
- "Architecture assumption wrong"
- "That's not how this works"
- "Unexpected infrastructure behavior"

**Scope:** Systematic process for discovering and correcting architectural misunderstandings about infrastructure

**Disambiguates From:**
- MW-006 (Flux Debugging) - This is for fundamental architecture gaps, not application-level debugging
- MW-002 (New Tool Development) - This is about fixing understanding, not building new tools

**Prerequisites:**
- Tool returns unexpected "not found" or "doesn't exist" errors
- User corrects AI's understanding of infrastructure
- Documentation conflicts with observed behavior

**Steps:**

#### 1. Acknowledge the Gap
**Actions:**
- State explicitly what you assumed
- Ask user to clarify actual architecture
- Don't proceed until you understand the correction
- Example: "I assumed K8s runs in production cluster, but you're saying it's in shared-service?"

**Validation:**
- User confirms your understanding of the correction

#### 2. Verify Understanding Incrementally
**Actions:**
- List what you now understand in bullet points
- Ask user: "Is this correct?"
- Get explicit confirmation before making changes

**Validation:**
- User says "yes" or "correct"

#### 3. Make Minimal Code Changes First
**Actions:**
- Update only constants/configuration (not logic)
- Example: Add missing cluster to `ALLOWED_CLUSTERS`
- Commit with clear message about what architectural understanding changed
- Message format: "Add [X] to [Y] - Architectural correction: [explanation]"

**Validation:**
- Code compiles/runs without errors
- Commit pushed successfully

#### 4. Test the Hypothesis
**Actions:**
- Try the operation that originally failed
- Verify the correction resolves the issue
- Document what you found in the test results

**Validation:**
- Operation succeeds that previously failed
- Results match user's expectations

#### 5. Update All Documentation
**Actions:**
- Update code comments (if architecture is documented there)
- Update session summary with corrected architecture section
- Update examples to show correct usage
- Update "Known Issues" section if applicable
- Add a new section documenting the discovery process

**Validation:**
- All documentation references the correct architecture
- No contradictions remain in docs

#### 6. Commit Documentation Separately
**Actions:**
- Commit all documentation changes together
- Clear commit message: "Document [architectural finding]"
- Include "why this matters" in the commit message body
- Reference the original error/confusion

**Validation:**
- Documentation commit pushed successfully
- Commit message is clear and searchable

#### 7. Create Reference for Future
**Actions:**
- Add to "Important Notes for AI Continuation" section
- Make the correction prominent and impossible to miss
- Include a "WARNING" or "NOTE" if the architecture is counter-intuitive
- Example: "NOTE: Production K8s runs in shared-service cluster, NOT in production cluster!"

**Validation:**
- Future AI sessions will see this warning
- The correction is documented in multiple places

**Outputs:**
- Updated code (minimal changes to configuration)
- Updated documentation (comprehensive)
- New section in session summary documenting the discovery
- Clear commit history showing the learning process

**Success Criteria:**
- [ ] Architectural correction verified with user
- [ ] Code updated incrementally and tested successfully
- [ ] All documentation reflects new understanding
- [ ] Session summary has dedicated section explaining discovery
- [ ] "Important Notes" section updated with warning
- [ ] Commit messages are clear and explain the correction
- [ ] Future sessions won't make the same assumption

**Example: This Session's 3-Cluster Discovery**

**Problem:** Tried to get production Flux logs but found no K8s nodes in production cluster

**Process Executed:**
1. ✅ Acknowledged gap: "I assumed 2 clusters (staging, production)"
2. ✅ User clarified: "Actually 3 clusters - K8s is in shared-service"
3. ✅ Made minimal change: Added "shared-service" to ALLOWED_TELEPORT_CLUSTERS
4. ✅ Fixed typo: "shared-services" → "shared-service"
5. ✅ Tested: Successfully listed nodes and retrieved logs
6. ✅ Updated docs: Added "V1c+ 3-Cluster Architecture Discovery" section
7. ✅ Created reference: Updated "Important Notes for AI Continuation"

**Result:** Complete architectural understanding documented, tested, and committed for future sessions.

---

#### 8. Documentation vs Resource Decision (New!)
**Actions:**
- When creating documentation (READMEs, guides), ask this checklist:
  - [ ] Does this contain structured data? (lists, tables, rules, configuration)
  - [ ] Should AI read this programmatically? (not just humans browsing)
  - [ ] Does this define a pattern/workflow/architecture?
  - [ ] Could this be configuration instead of prose?
- If YES to any → Create a YAML resource in `resources/`
- If NO → Keep as human-readable documentation (Markdown)

**Guidelines:**
- **Resources (YAML)** are for:
  - Configuration and data
  - Patterns and templates
  - Architectural definitions
  - Anything AI should query programmatically
  - Self-describing system information
  
- **Documentation (Markdown)** is for:
  - Narrative explanations
  - Philosophy and rationale
  - Human-friendly guides
  - Examples and tutorials

**Process:**
1. Create YAML resource in `resources/patterns/` or `resources/architecture/`
2. Add MCP resource endpoint in `platform_mcp.py` using `@mcp.resource()`
3. Test resource endpoint locally with `test_resources.py`
4. Commit and push changes to git
5. Deploy via `ansible-playbook playbooks/zed-mcp.yml`
6. Restart Zed completely (Cmd+Q and reopen)
7. Validate resource accessibility (see Known Limitations below)
8. Update README to reference the resource

**Example: This Session's State Management Pattern**

**Problem:** Created `.ephemeral/README.md` with lots of structured information

**Process Executed:**
1. ✅ Recognized pattern: README contains rules, directory structure, workflow steps
2. ✅ Asked checklist: "Is this structured data?" → YES
3. ✅ Created resource: `resources/patterns/state-management.yaml`
4. ✅ Added MCP endpoint: `@mcp.resource("workflow://patterns/state-management")`
5. ✅ Updated README: Shortened to reference the resource
6. ✅ Result: AI can now read the pattern programmatically

**Validation:**
- [ ] If structured data exists in docs, it should be in `resources/`
- [ ] READMEs should reference resources, not duplicate them
- [ ] Resource endpoint implemented with `@mcp.resource()`
- [ ] Local tests pass (`test_resources.py`)
- [ ] Deployed to ~/src/mcp-servers/platform-mcp-server
- [ ] Zed restarted to reload MCP server

**Known Limitations (2025-01-07):**

⚠️ **Zed's MCP client does not yet support resource discovery/reading**

**What works:**
- ✅ Server-side implementation (FastMCP fully supports resources)
- ✅ Local testing passes (`test_resources.py`)
- ✅ Resource files exist and are valid
- ✅ All `@mcp.resource()` endpoints correctly implemented

**What doesn't work in Zed:**
- ❌ Cannot access resources via `workflow://` URIs
- ❌ No resource listing capability
- ❌ Must use `read_file()` for filesystem access instead

**Root cause:** Zed's MCP client hasn't implemented resource protocol yet

**Workaround:** Use `read_file()` to access YAML files directly
- Example: `read_file("platform-mcp-server/resources/rules/design-checklist.yaml")`
- Works fine, just not automatic discovery
- Resources are ready for when Zed adds support

**Decision:** Keep resource implementation as-is (future-proof)
- Code aligns with MCP specification
- Will work automatically when Zed adds support
- No need to convert to tools
- Validated 2025-01-07 via comprehensive testing

**Validation Report:** See `.ephemeral/RESOURCE-TEST-CONTEXT.md` for full details

---

### MW-009: Tool Enhancement/Modification

**Trigger Phrases:**
- "Modify existing tool"
- "Enhance [tool name]"
- "Add parameter to [tool name]"
- "Fix bug in [tool name]"
- "Update [tool name]"

**Scope:** Modifying an existing MCP tool (not creating a new one)

**Disambiguates From:**
- MW-002 (which creates NEW tools, not modifies existing)
- Regular bug fixes (this is for intentional enhancements with validation)

**Prerequisites:**
- Existing tool to modify
- Clear understanding of what needs to change
- Know why the change is needed

**Steps:**

#### 1. Identify Impact Scope
**Actions:**
- Ask: "What tool are we modifying?"
- Ask: "What specifically needs to change?"
- Ask: "Why is this change needed?"
- Identify: Is this a bug fix, enhancement, or parameter addition?

**Validation:** Clear scope of change identified

#### 2. ⚠️ MANDATORY Backwards Compatibility Check
**⚠️ CRITICAL STEP - CANNOT BE SKIPPED ⚠️**

**Actions:**
- Check if tool is used by other tools or workflows
- Determine if change breaks existing callers
- If adding parameters:
  - [ ] Are new parameters optional with sensible defaults?
  - [ ] Do existing calls still work without changes?
- If modifying behavior:
  - [ ] Is old behavior preserved by default?
  - [ ] Is new behavior opt-in via parameter?
- If removing functionality:
  - [ ] Is there a deprecation period?
  - [ ] Are callers notified?

**Validation Criteria:**
- ✅ Existing callers continue to work unchanged (backwards compatible)
- ✅ OR breaking change is intentional and documented
- ✅ OR all callers updated in same commit

**If breaking change:**
- ⚠️ Document in commit message
- ⚠️ Update all callers
- ⚠️ Consider deprecation instead

#### 3. Design Validation (Same as MW-002 Step 2)
**Actions:**
1. Read design checklist: `platform-mcp-server/resources/rules/design-checklist.yaml`
2. Run through relevant checklist questions:
   - Configuration vs Code: Does change introduce hardcoding?
   - Dependencies: Does change add new dependencies?
   - Layer Placement: Does change violate layer boundaries?
   - Red Flags: Scan for anti-patterns

**Validation:** Change follows design principles

#### 4. Test Plan
**Actions:**
- [ ] Test existing behavior still works (backwards compatibility)
- [ ] Test new behavior works as expected
- [ ] Test edge cases and error conditions
- [ ] Test with and without new parameters (if applicable)

**Validation:** Comprehensive test plan documented

#### 5. Implement Change
**Actions:**
- Modify tool code
- Update docstring with:
  - New parameters and their defaults
  - Examples showing new behavior
  - Migration notes if breaking change
- Add inline comments explaining the change
- Update type hints

**Validation:** Code modified following standards

#### 6. Local Testing
**Actions:**
- Test in platform-mcp-server venv
- Execute test plan from Step 4
- Verify backwards compatibility
- Test new functionality

**Validation:** All tests pass

#### 7. Update Documentation
**Actions:**
- Update tool docstring (done in Step 5)
- Update SESSION-SUMMARY if significant change
- Add migration notes if needed
- Document in commit message:
  - What changed
  - Why it changed
  - Backwards compatibility status

**Validation:** Documentation complete

#### 8. Commit and Deploy
**Actions:**
- git add platform_mcp.py
- git commit with detailed message
- git push
- Deploy via ansible-playbook playbooks/zed-mcp.yml
- Restart Zed

**Validation:** Change deployed and available

**Outputs:**
- Modified tool with enhanced functionality
- Backwards compatibility maintained (or breaking changes documented)
- Updated documentation
- Test results

**Success Criteria:**
- [ ] Backwards compatibility maintained OR breaking change justified
- [ ] Design validation passed
- [ ] All tests pass (old behavior + new behavior)
- [ ] Documentation updated
- [ ] Deployed and working

**Example Execution:**
```
User: "Enhance list_flux_kustomizations to show suspend status"

AI: "Executing MW-009: Tool Enhancement/Modification

Step 1: Impact Scope
- Tool: list_flux_kustomizations()
- Change: Add optional parameter to show suspend status
- Why: Quick visibility without calling get_kustomization_details()

Step 2: Backwards Compatibility
- Adding parameter: show_suspend (default: False)
- Existing callers: Will work unchanged (default False)
- New behavior: Opt-in via show_suspend=True
✓ Backwards compatible

Step 3: Design Validation
- Reading design-checklist.yaml...
- Configuration vs Code: ✓ (parameter-based)
- Dependencies: ✓ (no new dependencies)
- Layer: ✓ (stays in TEAM layer)
- Red flags: ✓ (none detected)

Step 4: Test Plan
- Test without parameter (existing behavior)
- Test with show_suspend=False (same as default)
- Test with show_suspend=True (new behavior)

Step 5-8: Implementation, testing, deployment...
Done!"
```

**Related Workflows:**
- MW-002: Use for NEW tools
- MW-003: Use for testing existing tools
- MW-009: Use for MODIFYING tools

---

## Workflow Execution Examples

### Example 1: Thread Ending
```
User: "This thread is ending"

AI: "Executing MW-001: Thread Ending Summary
     
     Step 1/6: Assessing session state...
     - Implemented V1c (5 tools)
     - Committed 3 times
     - Deployed via Ansible
     ✓ Complete
     
     Step 2/6: Creating SESSION-SUMMARY-V1c.md...
     - Added 481 lines
     - Included all 14 tools
     - Documented testing status
     ✓ Complete
     
     Step 3/6: Documenting testing status...
     ✓ Complete
     
     Step 4/6: Creating next session checklist...
     ✓ Complete
     
     Step 5/6: Checking git state...
     - All changes committed
     - Git push succeeded
     ✓ Complete
     
     Step 6/6: Creating continuation instructions...
     ✓ Complete
     
     MW-001 Complete! 
     
     Summary: SESSION-SUMMARY-V1c.md
     Next session starts with: Read SESSION-SUMMARY-V1c.md
     Status: Ready for continuation"
```

### Example 2: Creating New Tool
```
User: "Create new MCP tool"

AI: "Executing MW-002: New MCP Tool Development
     
     Requirements gathering:
     1. What should this tool do?
     2. What parameters does it need?
     3. What does it return?
     4. Is this read-only or does it modify state?
     5. Which existing tools/primitives will it use?
     
     Please answer these questions so I can proceed."

User: [provides answers]

AI: "Checking for redundancy...
     Found similar tool: X
     Question: Should we extend X instead of creating new tool?
     
     [continues through workflow...]"
```

### Example 3: Ambiguous Request
```
User: "Add a tool"

AI: "I need to clarify: Are you asking to:
     - MW-002: Create a single new MCP tool
     - MW-007: Create a new category of tools
     
     Which workflow should I execute?"
```

---

## Maintenance

### Adding New Workflows
1. Use MW-005 to create the workflow
2. Assign next MW-ID
3. Test workflow execution
4. Update registry table

### Updating Existing Workflows
1. Note what changed in workflow
2. Update version/date
3. Test updated workflow
4. Document changes

### Deprecating Workflows
1. Mark as deprecated in registry
2. Add note explaining why
3. Point to replacement workflow
4. Keep in document for reference

---

## Quick Reference

### Starting a Workflow
Just say the trigger phrase naturally:
- "This thread is ending"
- "Create new MCP tool"
- "Deploy MCP changes"

### Stopping a Workflow
- "Cancel this workflow"
- "Never mind, let's do something else"

### Checking Available Workflows
- "What workflows are available?"
- "Show me the workflow registry"

### Getting Workflow Details
- "Explain the [workflow name] workflow"
- "What does MW-001 do?"

---

## Meta-Workflow Principles

1. **Explicit over Implicit** - Always confirm which workflow you're executing
2. **Fail Visible** - If a step fails, say so and pause
3. **User Control** - User can stop or redirect at any time
4. **Documentation First** - Workflows must be documented before use
5. **Continuous Improvement** - Update workflows based on execution experience
6. **No Ambiguity** - If request is ambiguous, ask before proceeding

---

**Last Updated:** 2024-11-02  
**Next Review:** After implementing 3 more workflows  
**Maintained By:** AI + User collaborative refinement