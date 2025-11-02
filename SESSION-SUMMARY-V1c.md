# Platform MCP Server - Session Summary (V1c Complete)

**Date:** 2024-11-02  
**Thread:** Building a Secure Platform MCP Server - V1c Implementation + Meta-Workflows  
**Status:** ✅ V1a Complete | ✅ V1b Complete | ✅ V1c Complete | ✅ Meta-Workflow System Created

---

## Executive Summary

Successfully built a complete **Platform MCP Server** with SSH-based remote command execution for Teleport-managed infrastructure. The server now provides full GitOps workflow management through Flux, enabling AI-assisted platform engineering operations.

**Key Achievements:** 
1. Created a composable architecture where low-level primitives (`run_remote_command()`) power high-level workflows (`list_flux_kustomizations()`, `suspend_flux_kustomization()`)
2. Established **Meta-Workflow System** - A "process bank" of repeatable workflows for consistent AI-assisted operations across sessions

---

## System Architecture

### The Real Workflow (Critical Understanding!)

**Initial Assumption (WRONG):**
- Kubernetes API exposed through Teleport kube proxy
- `tsh kube login` → local `kubectl` commands

**Actual Workflow (CORRECT):**
- Kubernetes API is NOT exposed externally
- Must SSH to nodes via Teleport: `tsh ssh user@node "kubectl ..."`
- Commands run as user `stephen.tan` with `sudo` for kubectl/flux

**Example:**
```bash
# The correct way to run Flux commands:
tsh ssh --cluster=staging stephen.tan@pi-k8-staging "sudo kubectl get kustomizations -A"
```

### Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│  HIGH-LEVEL TOOLS (Flux/K8s specific)              │
│  - list_flux_kustomizations()                       │
│  - suspend_flux_kustomization()                     │
│  - list_flux_sources()                              │
│  - get_flux_logs()                                  │
└─────────────────────────────────────────────────────┘
                        ↓ uses
┌─────────────────────────────────────────────────────┐
│  CORE PRIMITIVE                                     │
│  - run_remote_command(cluster, node, command)       │
│    → tsh ssh --cluster=X user@node "command"        │
└─────────────────────────────────────────────────────┘
                        ↓ requires
┌─────────────────────────────────────────────────────┐
│  DISCOVERY & VERIFICATION (V1a)                     │
│  - check_tsh_installed()                            │
│  - verify_teleport_compatibility()                  │
└─────────────────────────────────────────────────────┘
```

---

## Implemented Tools

### **V1a: Teleport Discovery & Version Management** ✅

1. **`check_tsh_installed()`** - Verify tsh CLI is installed
2. **`get_tsh_client_version()`** - Get installed tsh version
3. **`get_teleport_proxy_version(cluster)`** - Check server version
4. **`verify_teleport_compatibility()`** - Complete pre-flight check

**Key Insight:** Teleport is backwards compatible (old client works with new server) but NOT forwards compatible.

### **V1b: SSH Remote Command Execution** ✅

5. **`list_teleport_nodes(cluster, filter?)`** - List available SSH nodes
   - Example: Found 36 nodes in staging, 47 in production
   - Supports filtering: `filter='k8s'`

6. **`verify_ssh_access(cluster, node, user='root')`** - Test SSH connectivity

7. **`run_remote_command(cluster, node, command, user='root', timeout=30)`** - **THE CORE PRIMITIVE**
   - Execute ANY command on ANY node
   - Returns: `{success, stdout, stderr, exit_code, message}`
   - Security: Input validation, no shell injection, timeout protection

8. **`list_flux_kustomizations(cluster, node)`** - List all Flux Kustomizations
   - Uses `run_remote_command()` internally
   - Parses JSON output into structured data

9. **`reconcile_flux_kustomization(cluster, node, name, namespace='flux-system')`** - Trigger Flux reconciliation

### **V1c: Complete Flux Management Suite** ✅ (NEW!)

10. **`list_flux_sources(cluster, node)`** - List GitRepository sources
    - Shows what repos Flux watches
    - Returns: name, namespace, URL, ref, ready status, artifact revision

11. **`suspend_flux_kustomization(cluster, node, name, namespace='flux-system')`** - Pause reconciliation
    - Stops Flux from deploying changes
    - Use case: "Hold deployments while I debug"

12. **`resume_flux_kustomization(cluster, node, name, namespace='flux-system')`** - Resume reconciliation
    - Resumes a suspended kustomization
    - Use case: "Re-enable deployments"

13. **`get_flux_logs(cluster, node, component='kustomize-controller', tail=50)`** - View Flux logs
    - Components: kustomize-controller, source-controller, helm-controller, notification-controller
    - Returns last N lines of logs for debugging

14. **`get_kustomization_events(cluster, node, name, namespace='flux-system')`** - Get Kubernetes events
    - Shows recent events for a specific kustomization
    - Helpful for debugging failures

---

## Key Configuration Details

### Teleport Clusters
- **Staging:** `teleport.tw.ee:443`
- **Production:** `teleport.tw.ee:443`
- **Allowed clusters:** `["staging", "production"]` (hardcoded for security)

### Authentication
- **SSH User:** `stephen.tan` (not `root`!)
- **Kubectl/Flux:** Requires `sudo` prefix
- **Login:** `tsh login --proxy=teleport.tw.ee:443 --auth=okta {cluster}`

### Key Nodes
- **Staging K8s:** `pi-k8-staging` (172.31.50.195)
- **36 nodes in staging**, **47 nodes in production**

### Ansible Management
- **MCP Server Repo:** `~/personal/git/platform-mcp-server`
- **Ansible Repo:** `~/personal/git/ansible-mac`
- **Sync Command:** `ansible-playbook playbooks/zed-mcp.yml`
- **MCP Install Path:** `/Users/stephen.tan/src/mcp-servers/platform-mcp-server`

---

## Testing Results

### V1a Tests ✅
- tsh installed: `/usr/local/bin/tsh`
- Client version: `17.7.1`
- Staging proxy: `17.7.1` - Compatible ✅
- Production proxy: `17.7.1` - Compatible ✅

### V1b Tests ✅
- Listed 36 nodes in staging successfully
- SSH access verified to `pi-k8-staging`
- Remote command execution working
- Successfully retrieved Flux kustomizations via SSH

### V1c Implementation ✅
### V1c Tests ✅
- 5 new Flux management tools added
- Follow same security patterns as V1b
- All use `run_remote_command()` primitive
- Fixed to use `stephen.tan` user with `sudo` prefix
- Tested locally: list_flux_sources() found 1 GitRepository ✓
- Needs testing in Zed after restart

### Real-World Test (Staging)
```
Command: list_flux_kustomizations("staging", "pi-k8-staging")
Result: Found 20 kustomizations
Status: 
  - 17 healthy (85%)
  - 1 failed (ansible-awx-bootstrap)
  - 1 in progress (apps.tenable)
  - 1 blocked (apps - waiting on tenable)
```

---

## Security Design Principles

1. **Input Validation:** All cluster names validated against allow-list
2. **No Shell Injection:** Use `shlex.quote()` for user inputs
3. **No shell=True:** All subprocess calls use `shell=False`
4. **Timeout Protection:** Commands have configurable timeouts
5. **Defensive Programming:** Check prerequisites before operations
6. **Read-Only by Default:** Most tools are read-only queries
7. **Explicit State Changes:** Tools that modify state (suspend/resume) are clearly marked

### Safety Pattern
```python
# UNSAFE (DON'T DO THIS):
command = f"kubectl get {user_input}"  # Injection risk!

# SAFE (DO THIS):
safe_input = shlex.quote(user_input)
command = f"kubectl get {safe_input}"  # Injection-proof
```

---

## Development Workflow

### Making Changes

1. **Edit code** in `~/personal/git/platform-mcp-server/platform_mcp.py`
2. **Test locally:**
   ```bash
   cd ~/personal/git/platform-mcp-server
   source venv/bin/activate
   python test_teleport_v1b.py  # or test_teleport_v1c.py
   ```
3. **Commit & push:**
   ```bash
   git add platform_mcp.py
   git commit -m "Add feature X"
   git push
   ```
4. **Sync with Ansible:**
   ```bash
   cd ~/personal/git/ansible-mac
   ansible-playbook playbooks/zed-mcp.yml
   ```
5. **Restart Zed Preview** to reload MCP tools
6. **Test in Zed** with natural language prompts

### File Structure
```
platform-mcp-server/
├── platform_mcp.py          # Main MCP server (all tools here)
├── requirements.txt          # Python dependencies
├── test_teleport_tools.py   # V1a tests
├── test_teleport_v1b.py     # V1b tests
├── SESSION-SUMMARY.md       # Original summary (V1a+V1b)
├── SESSION-SUMMARY-V1c.md   # This file (complete state)
└── venv/                    # Python virtual environment
```

---

## Known Issues & Gotchas

### Issue 1: User Permissions
**Problem:** SSH as `root` fails with "access denied"  
**Solution:** Use `stephen.tan` user, prefix kubectl/flux with `sudo`  
**Status:** ✅ FIXED in all V1b and V1c tools (commit 2d9e1e8)

### Issue 2: K8s Node Discovery
**Problem:** No nodes with "k8s" in hostname  
**Solution:** Node is named `pi-k8-staging` (not `k8s-master-01`)

### Issue 3: Teleport Version Compatibility
**Problem:** Homebrew installs latest tsh, may break compatibility  
**Solution:** Use Ansible `teleport` role to pin version

### Issue 4: MCP Tool Updates
**Problem:** New tools not appearing in Zed  
**Solution:** Must restart Zed Preview after running Ansible sync  
**Current Status:** V1c tools deployed, awaiting Zed restart to test

### Issue 5: Meta-Workflow Memory
**Problem:** AI doesn't remember complex multi-step processes across sessions  
**Solution:** Created META-WORKFLOWS.md - A "process bank" with 7 documented workflows  
**Status:** ✅ Implemented MW-001 through MW-007

---

## What's Next? Future Work (V1d+)

### Option 1: V1d - Kubernetes Observability
- `get_pods(cluster, node, namespace?, label_selector?)`
- `get_pod_logs(cluster, node, pod, namespace, tail=100)`
- `describe_resource(cluster, node, resource_type, name, namespace)`
- `get_events(cluster, node, namespace?)`
- `exec_pod_command(cluster, node, pod, namespace, command)`

### Option 2: V1e - General System Administration
- `check_service_status(cluster, node, service)` - systemctl status
- `tail_logs(cluster, node, log_path, lines=100)` - tail logs
- `check_disk_usage(cluster, node)` - df -h
- `get_process_info(cluster, node, process_name)` - ps aux
- `restart_service(cluster, node, service)` - systemctl restart

### Option 3: V2 - Intelligent Workflows
- `diagnose_flux_issues(cluster, node)` - Auto-detect problems
- `safe_pod_restart(cluster, node, pod, namespace)` - With safeguards
- `deploy_with_approval(cluster, node, manifest)` - Interactive deployment
- `rollback_deployment(cluster, node, deployment, namespace)` - Undo changes

### Option 4: V1f - Helm Management
- `list_helm_releases(cluster, node, namespace?)`
- `get_helm_release_values(cluster, node, release, namespace)`
- `helm_rollback(cluster, node, release, namespace, revision?)`

---

## Testing Guide for Next Session

### Quick Start Tests
```bash
# In Zed Preview, try these prompts:

# V1b Tests (should already work)
"List nodes in staging cluster"
"Show nodes with 'pi' in the name"
"Show me Flux kustomizations on pi-k8-staging"

# V1c Tests (NEW - test these!)
"Show me Flux git sources on pi-k8-staging"
"Suspend the apps.tenable kustomization"
"Resume the apps.tenable kustomization"
"Show me kustomize-controller logs"
"Get events for the apps.tenable kustomization"
```

### Manual Testing
```bash
cd ~/personal/git/platform-mcp-server
source venv/bin/activate

# Test individual functions
python -c "
from platform_mcp import list_flux_sources
result = list_flux_sources('staging', 'pi-k8-staging')
print(result)
"
```

---

## Troubleshooting

### "tsh not installed"
```bash
cd ~/personal/git/ansible-mac
ansible-playbook playbooks/teleport.yml
```

### "Not logged into cluster"
```bash
tsh login --proxy=teleport.tw.ee:443 --auth=okta staging
```

### "Access denied to root@node"
**Fix:** Change `user="root"` to `user="stephen.tan"` in tool calls  
**Note:** This is already fixed in V1b+ tools (default user is configurable)

### "MCP tools not appearing in Zed"
1. Verify Ansible sync completed: `ansible-playbook playbooks/zed-mcp.yml`
2. Restart Zed Preview (⌘-Shift-P → "Zed: Restart")
3. Check MCP server is running: Look for `platform-tools` in MCP status

---

## Code Patterns & Examples

### Adding a New Tool

```python
@mcp.tool()
def my_new_tool(cluster: str, node: str, param: str) -> Dict[str, Any]:
    """
    Brief description of what this tool does.
    
    Args:
        cluster: Teleport cluster name ["staging", "production"]
        node: K8s node hostname
        param: Description of parameter
        
    Returns:
        dict: Result structure
        
    SECURITY NOTES:
    - Input validation
    - What safety measures used
    """
    
    # STEP 1: Validate inputs
    if cluster not in ALLOWED_TELEPORT_CLUSTERS:
        return {
            "success": False,
            "message": f"Invalid cluster: {cluster}",
            "ansible_command": None,
            "ansible_steps": [],
        }
    
    # STEP 2: Build command (with injection protection if needed)
    safe_param = shlex.quote(param)
    command = f"kubectl get {safe_param}"
    
    # STEP 3: Execute via SSH
    result = run_remote_command(cluster, node, command, user="root")
    
    # STEP 4: Return structured response
    if result["success"]:
        return {
            "success": True,
            "data": result["stdout"],
            "message": "✅ Success",
            "ansible_command": None,
            "ansible_steps": [],
        }
    else:
        return {
            "success": False,
            "message": f"❌ Failed: {result['message']}",
            "ansible_command": result.get("ansible_command"),
            "ansible_steps": result.get("ansible_steps", []),
        }
```

---

## Metrics & Progress

### Lines of Code
- `platform_mcp.py`: ~2,000 lines (well-documented)
- Test files: ~500 lines
- Total tools: 14 functions

### Tool Categories
- **Discovery/Verification:** 4 tools (V1a)
- **SSH/Remote Execution:** 5 tools (V1b)
- **Flux Management:** 5 tools (V1c)

### Coverage
- ✅ Teleport version management
- ✅ SSH node discovery & access
- ✅ Remote command execution
- ✅ Flux kustomization operations
- ✅ Flux source management
- ✅ Flux log viewing
- ⏳ Kubernetes pod management (future)
- ⏳ System administration (future)

---

## Important Notes for AI Continuation

1. **Always use the correct SSH user:** `stephen.tan`, not `root`
2. **kubectl/flux need sudo:** Prefix commands with `sudo`
3. **The k8s node is:** `pi-k8-staging` (not `k8s-master-01`)
4. **Always validate cluster names** against `ALLOWED_TELEPORT_CLUSTERS`
5. **Use `shlex.quote()`** for user-provided strings in commands
6. **Test changes locally first** before committing
7. **Run Ansible sync** after git push to deploy changes
8. **Restart Zed Preview** to reload MCP tools
9. **All tools must return** the standard dict format with `success`, `message`, `ansible_command`, `ansible_steps`
10. **Use `run_remote_command()`** as the primitive for all remote operations

---

## Quick Reference Commands

```bash
# Development
cd ~/personal/git/platform-mcp-server
source venv/bin/activate
python test_teleport_v1c.py

# Deployment
git add -A && git commit -m "message" && git push
cd ~/personal/git/ansible-mac
ansible-playbook playbooks/zed-mcp.yml

# Teleport
tsh login --proxy=teleport.tw.ee:443 --auth=okta staging
tsh ls --cluster staging
tsh ssh --cluster staging stephen.tan@pi-k8-staging

# Testing in Zed
"List nodes in staging"
"Show Flux state on pi-k8-staging"
"Suspend apps.tenable kustomization"
"Show flux logs"
```

---

## Success Criteria for V1c ✅

- [x] All V1c tools implemented
- [x] Security patterns followed (input validation, shlex.quote)
- [x] All tools use run_remote_command() primitive
- [x] Comprehensive documentation in docstrings
- [x] Session summary created for continuation
- [x] User authentication fixed (stephen.tan with sudo)
- [x] Committed and deployed via Ansible
- [x] Local testing passed (list_flux_sources works)
- [ ] V1c tools tested in Zed Preview (requires Zed restart - next session)

## Success Criteria for Meta-Workflow System ✅

- [x] META-WORKFLOWS.md created (720 lines)
- [x] 7 workflows documented (MW-001 through MW-007)
- [x] Trigger phrases defined for each workflow
- [x] Disambiguation rules established
- [x] Step-by-step execution instructions
- [x] Examples of workflow execution
- [x] Registry table for tracking workflows
- [x] Committed and pushed to git

---

## Git Commits This Session

1. **ba4b69b** - Add V1b: SSH-based remote command execution via Teleport
2. **921a4f0** - Add V1c: Complete Flux management suite
3. **2d9e1e8** - Fix V1c tools: use stephen.tan user with sudo for kubectl/flux
4. **9400e3c** - Add META-WORKFLOWS.md: Process bank for repeatable AI workflows

## Final Session Metrics

- **Lines Added:** ~1,600 lines (V1c tools + META-WORKFLOWS.md + fixes)
- **Tools Implemented:** 5 (V1c Flux management suite)
- **Workflows Documented:** 7 (MW-001 through MW-007)
- **Git Commits:** 4
- **Token Usage:** ~110k/1M

---

**Ready for Next Session:** 
1. **Restart Zed Preview** (⌘-Shift-P → "Zed: Restart")
2. **Test V1c tools** with natural language prompts
3. **Use Meta-Workflows:** Try "This thread is ending" in future sessions
4. **Then proceed to:** V1d (K8s Observability) or V1e (System Administration)

**First Command Next Session:**
```
"Show me Flux git sources on pi-k8-staging"
```

**Estimated Time:**
- V1c testing: 10-15 minutes
- V1d implementation: 30-45 minutes
- Using meta-workflows: Instant execution

---

## How to Use Meta-Workflows (NEW!)

Just say the trigger phrase:
- **"This thread is ending"** → MW-001: Creates comprehensive session summary
- **"Create new MCP tool"** → MW-002: Full tool development lifecycle
- **"Deploy MCP changes"** → MW-004: Git → Ansible → Zed restart workflow
- **"Create new meta-workflow"** → MW-005: Add new repeatable process

See **META-WORKFLOWS.md** for complete workflow registry and documentation.

---

**Session Complete!** All changes committed, documented, and ready for continuation. 🎉