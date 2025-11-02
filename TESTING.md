# Testing Guide - Platform MCP Server

This guide covers testing the Platform MCP Server in both Ansible-managed and manual configurations.

## 🏗️ Architecture Overview

The Platform MCP Server follows a layered architecture when installed via Ansible:

```
Layer 1: System Packages (node, uv, volta, git)
    ↓
Layer 2: MCP Dependencies (clone repo, create .venv, install deps)
    ↓
Layer 3: Zed Configuration (configure settings.json)
    ↓
Zed Editor → Platform Tools MCP → Your Infrastructure
```

## ✅ Recommended: Ansible-Managed Testing

### Prerequisites Check

```bash
# Verify Ansible is installed
ansible --version

# Verify you have the ansible-mac repository
ls ~/personal/git/ansible-mac/

# Verify Zed is installed
ls ~/.config/zed/
```

### Layer-by-Layer Testing

#### Layer 1: System Packages

Test that required system tools are installed:

```bash
cd ~/personal/git/ansible-mac
ansible-playbook playbooks/test-mcp-prerequisites.yml
```

**Expected Output**:
```
✓ node v23.11.0 installed
✓ npx installed
✓ uv 0.8.19 installed
✓ volta 2.0.2 installed
✓ git 2.48.1 installed
```

#### Layer 2: MCP Dependencies

Test that the repository is cloned and Python environment is set up:

```bash
cd ~/personal/git/ansible-mac
ansible-playbook playbooks/test-mcp-dependencies.yml
```

**Expected Output**:
```
TASK [Check platform-mcp-server repository exists]
ok: [localhost]

TASK [Check platform-mcp-server .venv exists]
ok: [localhost]

TASK [Verify Python executable in .venv]
ok: [localhost] => Python 3.11.13
```

**Manual Verification**:
```bash
# Check repository was cloned
ls -la ~/src/mcp-servers/platform-mcp-server/

# Check .venv was created
ls -la ~/src/mcp-servers/platform-mcp-server/.venv/

# Test Python and imports
~/src/mcp-servers/platform-mcp-server/.venv/bin/python -c "import mcp; import fastmcp; print('✓ Dependencies installed')"
```

#### Layer 3: Zed Configuration

Test that Zed's settings.json is configured correctly:

```bash
cd ~/personal/git/ansible-mac
ansible-playbook playbooks/test-zed-mcp.yml --tags platform-tools
```

**Manual Verification**:
```bash
# Check settings.json has platform-tools
cat ~/.config/zed/settings.json | grep -A 8 "platform-tools"
```

**Expected Output**:
```json
"platform-tools": {
  "command": "/Users/stephen.tan/src/mcp-servers/platform-mcp-server/.venv/bin/python",
  "args": [
    "/Users/stephen.tan/src/mcp-servers/platform-mcp-server/platform_mcp.py"
  ],
  "env": {
    "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
  }
}
```

### Full Stack Integration Test

Run the complete setup from scratch:

```bash
cd ~/personal/git/ansible-mac

# Full deployment
ansible-playbook playbooks/zed-mcp.yml

# Or just platform-tools
ansible-playbook playbooks/zed-mcp.yml --tags platform-tools
```

**Success Criteria**:
- ✅ No failed tasks
- ✅ Repository cloned to `~/src/mcp-servers/platform-mcp-server/`
- ✅ `.venv` directory exists with Python and dependencies
- ✅ `settings.json` contains platform-tools configuration
- ✅ Second run shows minimal changes (idempotent)

### Idempotency Test

Critical requirement: No changes on repeated runs (except temp files)

```bash
cd ~/personal/git/ansible-mac

# First run (should make changes)
ansible-playbook playbooks/zed-mcp.yml --tags platform-tools

# Second run (should be idempotent)
ansible-playbook playbooks/zed-mcp.yml --tags platform-tools
```

**Expected Second Run Output**:
```
PLAY RECAP *********************************************************************
localhost : ok=X changed=0 unreachable=0 failed=0 skipped=Y rescued=0 ignored=0
```

Note: Some temp file changes are OK, but no repository/venv changes.

## 🧪 Tool Functionality Testing

### Local Test Script

Test the MCP server directly without Zed:

```bash
cd ~/src/mcp-servers/platform-mcp-server
source .venv/bin/activate
python test_server.py
```

**Expected Output**:
```
✅ MCP Server module loaded successfully!

🧪 Testing list_kube_contexts tool directly...
✅ Success! Found 3 Kubernetes context(s):
  - bzero-root@home
  - default
  - k3s-ansible
```

### Test in Zed Editor

1. **Restart Zed** (MCP servers are loaded on startup)
   ```bash
   # Kill Zed if running
   pkill -9 Zed
   
   # Start Zed
   open -a Zed
   ```

2. **Open the Agent panel**
   - Keyboard: `Cmd+Shift+A`
   - Or click the assistant icon

3. **Verify server is connected**
   - Look for "platform-tools" in the context servers list
   - Should show green indicator if running

4. **Test with a prompt**:
   ```
   List my Kubernetes contexts using the platform-tools MCP server
   ```

5. **Expected behavior**:
   - AI recognizes the `list_kube_contexts` tool
   - Calls the tool automatically
   - Returns your kubectl contexts: `bzero-root@home`, `default`, `k3s-ansible`

### Check Zed Logs

If the MCP server isn't working:

```bash
# View recent logs
tail -f ~/Library/Logs/Zed/Zed.log

# Search for platform-tools errors
grep -i "platform-tools\|platform_mcp" ~/Library/Logs/Zed/Zed.log
```

## 🐛 Troubleshooting

### Server Not Appearing in Zed

**Problem**: platform-tools not in context servers list

**Diagnosis**:
```bash
# Check if configured
cat ~/.config/zed/settings.json | grep -A 5 "platform-tools"

# Should show configuration, if not:
ansible-playbook ~/personal/git/ansible-mac/playbooks/zed-mcp.yml --tags platform-tools

# Restart Zed
pkill -9 Zed && open -a Zed
```

### Tool Returns Error

**Problem**: MCP server crashes or returns errors

**Diagnosis**:
```bash
# Test directly
cd ~/src/mcp-servers/platform-mcp-server
source .venv/bin/activate
python platform_mcp.py

# Check for import errors
python -c "import mcp; import fastmcp; print('OK')"

# Reinstall dependencies if needed
uv pip install -r requirements.txt
```

### kubectl Not Found

**Problem**: Tool returns "kubectl command not found"

**Diagnosis**:
```bash
# Check PATH in settings
cat ~/.config/zed/settings.json | jq '.context_servers["platform-tools"].env.PATH'

# Should include: /opt/homebrew/bin

# If missing, reconfigure
ansible-playbook ~/personal/git/ansible-mac/playbooks/zed-mcp.yml --tags platform-tools
```

### Python Version Issues

**Problem**: Wrong Python version or missing .venv

**Diagnosis**:
```bash
# Check Python in venv
~/src/mcp-servers/platform-mcp-server/.venv/bin/python --version

# Should be Python 3.11.x

# If wrong, recreate
cd ~/src/mcp-servers/platform-mcp-server
rm -rf .venv
uv venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Ansible Changes Every Run (Not Idempotent)

**Problem**: Second run shows changes

**Diagnosis**:
```bash
# Check what's changing
ansible-playbook ~/personal/git/ansible-mac/playbooks/zed-mcp.yml --tags platform-tools --diff

# Common causes:
# - Git repo has local modifications (use git clean)
# - settings.json formatting issue (use jq to reformat)
# - Temp files (ignore these)
```

## 📋 Testing Checklist

Before considering platform-tools "working":

- [ ] System packages installed (node, uv, git)
- [ ] Repository cloned to correct location
- [ ] Python .venv created with correct version
- [ ] Dependencies installed (mcp, fastmcp)
- [ ] Zed settings.json contains platform-tools
- [ ] PATH configured correctly in settings
- [ ] Test script runs without errors
- [ ] Zed shows platform-tools in context servers
- [ ] Tool responds to prompts in Zed
- [ ] kubectl contexts returned correctly
- [ ] Second Ansible run is idempotent
- [ ] Zed logs show no errors

## 🚀 Advanced Testing

### Test with Mock kubectl

Test without actual kubectl:

```bash
cd ~/src/mcp-servers/platform-mcp-server

# Create mock kubectl script
cat > /tmp/kubectl << 'EOF'
#!/bin/bash
echo "test-context-1"
echo "test-context-2"
EOF
chmod +x /tmp/kubectl

# Test with mock
PATH=/tmp:$PATH python test_server.py
```

### Test Error Handling

```bash
cd ~/src/mcp-servers/platform-mcp-server
source .venv/bin/activate

# Test with kubectl unavailable
PATH=/usr/bin python test_server.py
# Should return: "Error: kubectl command not found..."
```

### Load Testing (Multiple Calls)

```bash
cd ~/src/mcp-servers/platform-mcp-server
source .venv/bin/activate

python << 'EOFTEST'
from platform_mcp import list_kube_contexts
import time

# Test 10 rapid calls
for i in range(10):
    start = time.time()
    result = list_kube_contexts()
    elapsed = time.time() - start
    print(f"Call {i+1}: {elapsed:.3f}s - {len(result.splitlines())} contexts")
EOFTEST
```

## 📊 Performance Expectations

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Ansible first run | 2-5 minutes | Clones repo, creates venv, installs deps |
| Ansible second run | 10-30 seconds | Idempotent check only |
| Tool execution | <100ms | Direct kubectl call |
| Zed startup with MCP | 2-5 seconds | Loads all MCP servers |

## 🔄 Update Testing

When updating the MCP server:

```bash
# Pull latest from GitHub
cd ~/src/mcp-servers/platform-mcp-server
git pull

# Reinstall dependencies (if requirements.txt changed)
source .venv/bin/activate
uv pip install -r requirements.txt

# Or use Ansible to update
cd ~/personal/git/ansible-mac
ansible-playbook playbooks/zed-mcp.yml --tags mcp-dependencies,platform-tools

# Test changes
cd ~/src/mcp-servers/platform-mcp-server
python test_server.py

# Restart Zed
pkill -9 Zed && open -a Zed
```

## 📚 Related Documentation

- Main README: `~/src/mcp-servers/platform-mcp-server/README.md`
- Ansible MCP Setup: `~/personal/git/ansible-mac/docs/ZED_MCP_SETUP.md`
- MCP Dependencies Role: `~/personal/git/ansible-mac/roles/mcp-dependencies/README.md`
- Zed MCP Role: `~/personal/git/ansible-mac/roles/zed-mcp/README.md`

---

**Quick Test Command**:
```bash
# Full test
cd ~/personal/git/ansible-mac && \
  ansible-playbook playbooks/test-mcp-dependencies.yml && \
  ansible-playbook playbooks/test-zed-mcp.yml --tags platform-tools && \
  cd ~/src/mcp-servers/platform-mcp-server && \
  source .venv/bin/activate && \
  python test_server.py
```

**Expected**: All tests pass ✅