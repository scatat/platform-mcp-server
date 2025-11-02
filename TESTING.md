# Testing Guide

## Quick Verification

Run the test script to verify the MCP server works:

```bash
source venv/bin/activate
python test_server.py
```

Expected output:
```
✅ MCP Server module loaded successfully!

🧪 Testing list_kube_contexts tool directly...
✅ Success! Found 3 Kubernetes context(s):
  - bzero-root@home
  - default
  - k3s-ansible
```

## Testing in Zed

1. **Restart Zed** - MCP servers are loaded on startup
2. **Open the Agent panel** (Cmd+Shift+A or click the assistant icon)
3. **Verify the server is connected**:
   - Look for "platform-tools" in the context servers list
   - You should see a green indicator if it's running

4. **Test the tool with a prompt**:
   ```
   List my Kubernetes contexts using the platform-tools MCP server
   ```

5. **Expected behavior**:
   - The AI should recognize the `list_kube_contexts` tool
   - It should call the tool and return your kubectl contexts
   - You should see: `bzero-root@home`, `default`, `k3s-ansible`

## Troubleshooting

### Server not appearing in Zed

1. Check Zed logs:
   ```bash
   tail -f ~/Library/Logs/Zed/Zed.log
   ```

2. Verify configuration:
   ```bash
   cat ~/.config/zed/settings.json | grep -A 8 "platform-tools"
   ```

3. Verify Python path:
   ```bash
   /Users/stephen.tan/personal/git/platform-mcp-server/venv/bin/python --version
   ```

### Tool not working

1. Test manually:
   ```bash
   cd /Users/stephen.tan/personal/git/platform-mcp-server
   source venv/bin/activate
   python platform_mcp.py
   ```

2. Check kubectl access:
   ```bash
   kubectl config get-contexts -o name
   ```

### Common Issues

| Issue | Solution |
|-------|----------|
| "kubectl not found" | Add kubectl to PATH in env settings |
| "Permission denied" | Check file permissions: `chmod +x platform_mcp.py` |
| "Module not found" | Activate venv: `source venv/bin/activate` |
| Server won't start | Check Python version: `python3 --version` (need 3.8+) |

## Next Steps

Once this tool works, you're ready to build V2 tools!

Suggested next tools:
- `run_flux_on_prod` - Execute Flux reconciliation
- `list_ansible_packages` - Show packages in Ansible inventory
- `get_teleport_status` - Check Teleport connection status
