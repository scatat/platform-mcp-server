# Session Summary: Platform MCP Server Development

**Date**: 2024-11-02  
**Status**: V1a Complete - Ready for V1b  
**Next Session Goal**: Build V1b Teleport Session Management Tools

---

## 🎯 What We Accomplished

### 1. Created Platform MCP Server Repository
- **Repo**: https://github.com/scatat/platform-mcp-server
- **Location**: `~/src/mcp-servers/platform-mcp-server/` (Ansible-managed)
- **Configured in**: Zed Preview via Ansible

### 2. Implemented V1 Tools (Read-Only Discovery)
✅ `list_kube_contexts()` - List Kubernetes contexts

### 3. Implemented V1a Tools (Teleport Version Management)
✅ `check_tsh_installed()` - Verify tsh binary exists  
✅ `get_tsh_client_version()` - Get client version  
✅ `get_teleport_proxy_version(cluster)` - Check server version per cluster  
✅ `verify_teleport_compatibility()` - Complete pre-flight check with guidance

**Key Feature**: All tools return `ansible_command` and `ansible_steps` when fixes are needed.

### 4. Created Ansible Teleport Role
- **Location**: `ansible-mac/roles/teleport/`
- **Playbook**: `ansible-mac/playbooks/teleport.yml`
- **Purpose**: Version-pinned tsh installation (currently v17.7.1)
- **Status**: ✅ Working - tsh upgraded from 16.4.8 to 17.7.1

### 5. Established Critical Patterns

#### The MCP Dependency Contract
```yaml
Rule: "Awareness and Guidance - Installation via Ansible"

MCP Server Responsibilities:
  ✅ Verify tools are installed
  ✅ Check versions are compatible
  ✅ Provide clear error messages
  ✅ SUGGEST specific Ansible commands to fix issues
  ✅ Provide context-aware guidance
  ❌ NEVER install or update tools directly
  
Ansible Responsibilities:
  ✅ Install all external dependencies
  ✅ Manage tool versions
  ✅ Handle OS-specific installation
  ✅ Ensure tools are in PATH
```

#### Workflow We Demonstrated
1. MCP tool detects issue (version mismatch)
2. Returns exact Ansible command to fix it
3. User approves
4. AI executes: `ansible-playbook playbooks/teleport.yml --ask-become-pass`
5. MCP tool verifies fix succeeded

---

## 📋 Current System State

### Teleport Setup
- **Client Version**: 17.7.1 ✅
- **Staging Proxy**: 17.7.1 ✅
- **Production Proxy**: 17.7.1 ✅
- **Status**: Perfect compatibility, ready for Flux operations

### MCP Tools Available in Zed Preview
1. `list_kube_contexts`
2. `check_tsh_installed`
3. `get_tsh_client_version`
4. `get_teleport_proxy_version`
5. `verify_teleport_compatibility`

### File Locations
```
~/personal/git/ansible-mac/          # Ansible infrastructure
  ├── roles/teleport/                # Teleport installation role
  └── playbooks/teleport.yml         # Teleport playbook

~/personal/git/platform-mcp-server/  # Git repository
~/src/mcp-servers/platform-mcp-server/ # Ansible-managed (active)
  ├── platform_mcp.py                # Main MCP server
  ├── .venv/                         # Python environment
  └── requirements.txt

~/.config/zed/settings.json          # Zed configuration
```

---

## 🎯 The Original Goal (Context)

Build an MCP server to handle **Flux operations in work environment** which requires:

1. Know target environment (staging/production) ✅ (allow-list exists)
2. Verify Teleport login ⬅️ **NEXT: V1b**
3. Verify k8s cluster visibility ⬅️ **NEXT: V1b**
4. Execute Flux command via Teleport ⬅️ **FUTURE: V2**

**Current Progress**: We've completed the foundation (V1a) - version management and compatibility checks.

---

## 📝 Next Steps: V1b Tools

### Build These Tools Next (Read-Only Session Management)

```python
1. list_teleport_sessions() -> dict
   """
   Check if logged into Teleport and list active sessions.
   Prerequisite: Calls verify_teleport_compatibility() first
   Returns: {
       "logged_in": bool,
       "clusters": List[str],
       "current_cluster": str,
       "valid_until": str,
       "roles": List[str],
       "raw_status": str
   }
   """

2. list_teleport_clusters() -> List[str]
   """
   List available Teleport clusters.
   Returns: ["staging", "production"]
   """

3. get_teleport_kube_clusters(cluster: str) -> List[str]
   """
   List Kubernetes clusters available in a Teleport cluster.
   Input validation: cluster must be in ["staging", "production"]
   Returns: List of k8s cluster names
   """

4. verify_kube_access(cluster: str, kube_cluster: str) -> bool
   """
   Test if we can access a specific k8s cluster via Teleport.
   Returns: True if `kubectl get nodes` succeeds, False otherwise
   """

5. list_flux_kustomizations(cluster: str, kube_cluster: str) -> str
   """
   List Flux Kustomizations in a cluster (via Teleport).
   Returns: Output of `flux get kustomizations`
   """
```

---

## 🔑 Key Constants & Configuration

### In platform_mcp.py
```python
ANSIBLE_MAC_PATH = "~/personal/git/ansible-mac"
ALLOWED_TELEPORT_CLUSTERS = ["staging", "production"]
TSH_BINARY_PATH = "/usr/local/bin/tsh"
```

### Teleport Cluster Config
```yaml
teleport_clusters:
  - name: staging
    proxy: "teleport.tw.ee:443"
  - name: production
    proxy: "teleport.tw.ee:443"
```

---

## 🎓 Critical Learnings & Patterns

### 1. Editor Context
**USER USES ZED PREVIEW (not regular Zed)**
- Both read same config: `~/.config/zed/settings.json`
- Separate processes - must restart **Zed Preview** to reload MCP tools

### 2. Repository Sync Issue
**There are TWO locations**:
- `~/personal/git/platform-mcp-server/` - Git repo for development
- `~/src/mcp-servers/platform-mcp-server/` - Ansible-managed (active in Zed)

**Workflow**:
1. Edit in git repo
2. Commit and push
3. Run: `ansible-playbook playbooks/zed-mcp.yml --tags mcp-dependencies`
4. Ansible pulls latest from GitHub

### 3. Tool Registration
Tools are registered with `@mcp.tool()` decorator. After updating:
- Commit to git
- Ansible pulls update
- Restart Zed Preview
- Verify with: `cd ~/src/mcp-servers/platform-mcp-server && .venv/bin/python -c "import platform_mcp; print(len(platform_mcp.mcp._tool_manager._tools))"`

### 4. Testing Pattern
```bash
cd ~/src/mcp-servers/platform-mcp-server
.venv/bin/python -c "
import platform_mcp
for tool in platform_mcp.mcp._tool_manager._tools.keys():
    print(f'  - {tool}')
"
```

---

## 📚 Important Documentation Files

### In ansible-mac repo
- `ansible-mac/.context/CRITICAL-INFO.md` - System details for AI agents
- `ansible-mac/roles/teleport/README.md` - Teleport role documentation
- `ansible-mac/roles/teleport/defaults/main.yml` - Version configuration

### In platform-mcp-server repo
- `platform-mcp-server/README.md` - Main project documentation
- `platform-mcp-server/platform_mcp.py` - Source code with detailed comments

---

## 🔒 Security Principles (Established)

1. **No `shell=True`**: Always use `subprocess.run(..., shell=False)`
2. **Input Validation**: All user inputs validated against allow-lists
3. **Defensive Programming**: Check prerequisites before operations
4. **Clear Guidance**: Return actionable Ansible commands when issues found
5. **Read-Only First**: V1/V1a/V1b are all read-only discovery tools

---

## 💡 Communication Style with User

- **Background**: Platform engineer (expert in Ansible, Git, k8s) learning Python
- **Approach**: Use platform engineering analogies
  - Decorator = "wrapper script"
  - Docstring = "README.md for function"
  - Type hints = "variable declarations"
- **Expectations**: Security-first, idempotent, clear documentation

---

## 🚀 How to Continue Next Session

### Immediate Next Action
Start building V1b tool #1: `list_teleport_sessions()`

### Code Template to Start With
```python
@mcp.tool()
def list_teleport_sessions() -> Dict[str, Any]:
    """
    Check if logged into Teleport and list active sessions.
    
    This is a READ-ONLY tool. It checks session status without modifying anything.
    
    ANALOGY: Like running `tsh status` to see your current login state.
    
    Returns:
        dict: Session information or error with guidance
        {
            "logged_in": bool,
            "clusters": List[str],
            "current_cluster": str,
            "valid_until": str,
            "expires_in": str,
            "roles": List[str],
            "logins": List[str],
            "message": str,
            "ansible_command": str,  # If tsh issues found
            "ansible_steps": List[str]
        }
    
    SECURITY NOTES:
    - Read-only operation (doesn't modify sessions)
    - Calls verify_teleport_compatibility() first
    - Parses `tsh status` output safely
    """
    
    # STEP 1: Verify tsh is installed and compatible
    compat_check = verify_teleport_compatibility()
    if not compat_check["compatible"]:
        return {
            "logged_in": False,
            "message": "Cannot check sessions - tsh compatibility issues",
            "ansible_command": compat_check.get("ansible_command"),
            "ansible_steps": compat_check.get("ansible_steps", [])
        }
    
    # STEP 2: Run tsh status
    # Implementation here...
```

### Test Command for New Tool
```
Check if I'm logged into Teleport and show my session status
```

---

## 🎯 Success Criteria for V1b

By end of next session, user should be able to ask:
- "Am I logged into Teleport?"
- "Which Teleport clusters can I access?"
- "What Kubernetes clusters are available in staging?"
- "Can I access the production k8s cluster?"
- "Show me the Flux Kustomizations in staging"

All tools return:
- ✅ Clear status information
- ✅ Ansible guidance if prerequisites missing
- ✅ Detailed docstrings for AI understanding
- ✅ Security-first implementation

---

## 📌 Remember

1. **Always commit to git repo first**, then run Ansible to sync
2. **Restart Zed Preview** after Ansible updates
3. **Test tools** before calling them complete
4. **Follow the patterns** established in V1a tools
5. **User can approve Ansible playbook execution** when needed

---

**Ready to build V1b!** 🚀