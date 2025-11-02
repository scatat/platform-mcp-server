# Meta-Workflows: Process Bank for Platform Engineering

**Purpose:** A "memory bank" of commonly-used processes and workflows for AI-assisted platform engineering. This allows you to invoke complex multi-step processes with simple natural language triggers.

**Date Created:** 2024-11-02  
**Date Updated:** 2024-11-02 (Added auto-discovery via MCP tools)  
**Status:** Living Document

## 🔍 Auto-Discovery (New!)

As of V1c, meta-workflows are **automatically discoverable** via the MCP server:

- **Tool: `list_meta_workflows()`** - Returns structured list of all workflows with trigger phrases
- **Resource: `workflow://meta-workflows`** - Exposes this entire document as readable context

**What This Means:**
- The AI can now discover workflows without being told they exist
- No more "chicken-and-egg" problem in new sessions
- The system is self-documenting

**How to Use:**
```
# AI can call this automatically to discover workflows
list_meta_workflows()

# Returns: List of 7 workflows with IDs, names, triggers, and status
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

### Active Workflows

| ID | Name | Trigger | Status | Last Updated |
|----|------|---------|--------|--------------|
| MW-001 | Thread Ending Summary | "This thread is ending" | Active | 2024-11-02 |
| MW-002 | New MCP Tool Development | "Create new MCP tool" | Active | 2024-11-02 |
| MW-003 | MCP Tool Testing Suite | "Test MCP tools" | Active | 2024-11-02 |
| MW-004 | Deploy MCP Changes | "Deploy MCP changes" | Active | 2024-11-02 |
| MW-005 | Create Meta-Workflow | "Create new meta-workflow" | Active | 2024-11-02 |
| MW-006 | Flux Debugging Session | "Debug Flux issues" | Draft | 2024-11-02 |
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

#### 2. Create/Update SESSION-SUMMARY Document
**Actions:**
- Create new or update existing SESSION-SUMMARY-*.md
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
- Use current session summary as template
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
- SESSION-SUMMARY-*.md (comprehensive state document)
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
     1. Review what we accomplished...
     2. Create SESSION-SUMMARY-V1c.md...
     3. Document testing status...
     4. Define next steps...
     Done! Summary created with 481 lines of documentation."
```

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

#### 2. Check for Redundancy
**Actions:**
- Review existing tools in platform_mcp.py
- Search for similar functionality
- Ask: "Tool X does something similar. Should we extend it instead?"
- Confirm: "This is a new tool, not a modification of existing"

**Validation:** No duplicate functionality

#### 3. Security Review
**Actions:**
- Identify all user inputs
- Determine if inputs go into commands
- Plan shlex.quote() usage
- Verify cluster name validation
- Check if sudo/privilege escalation needed
- Document security measures in docstring

**Validation:** Security requirements identified

#### 4. Implement Tool
**Actions:**
- Follow existing code patterns (see SESSION-SUMMARY)
- Use @mcp.tool() decorator
- Add comprehensive docstring with examples
- Implement input validation
- Use run_remote_command() or other primitives
- Return standard dict format: {success, message, ansible_command, ansible_steps, ...}
- Add inline comments explaining each step

**Validation:** Code follows established patterns

#### 5. Local Testing
**Actions:**
- Test in platform-mcp-server venv
- Test with valid inputs
- Test with invalid inputs
- Test error cases
- Verify return format matches spec

**Validation:** Tool works as expected locally

#### 6. Commit Changes
**Actions:**
- git add platform_mcp.py
- git commit with descriptive message
- git push

**Validation:** Changes in git history

#### 7. Deploy via Ansible
**Actions:**
- cd ~/personal/git/ansible-mac
- ansible-playbook playbooks/zed-mcp.yml
- Verify sync completed

**Validation:** Ansible reports success

#### 8. Integration Testing
**Actions:**
- Restart Zed Preview
- Test tool with natural language prompts
- Verify tool appears in MCP tool list
- Test with real cluster/node

**Validation:** Tool works in Zed Preview

#### 9. Update Documentation
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