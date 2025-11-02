# Session Documentation

This directory contains **persistent session summaries** - final documentation of completed development sessions.

**📚 This is git-tracked permanent documentation** (unlike `.ephemeral/` which is gitignored)

## Structure

```
docs/sessions/
├── README.md              # This file
├── V1a/
│   └── FINAL-SUMMARY.md  # V1a: Teleport Version Management
├── V1c/
│   └── FINAL-SUMMARY.md  # V1c: Flux/K8s Tools
└── V1d/
    └── FINAL-SUMMARY.md  # V1d: (future sessions)
```

## Quick Reference

✅ **DO Store Here:**
- Completed session summaries
- Key decisions and rationale
- Testing results and baselines
- Lessons learned

❌ **DON'T Store Here:**
- Working notes → `.ephemeral/sessions/`
- Test outputs → `.ephemeral/tests/`
- Drafts or WIP → `.ephemeral/`

## Detailed Documentation

This directory follows the **Session Documentation Pattern**.

For complete documentation, see:
- **MCP Resource**: `workflow://patterns/session-documentation`
- **File**: `resources/patterns/session-documentation.yaml`

That resource contains:
- FINAL-SUMMARY.md template with all sections
- Naming conventions (VXx/ vs YYYY-MM-DD/)
- Extraction rules from ephemeral notes
- Quality checks for completeness
- Anti-patterns to avoid

## Creating a Session Summary

Use **MW-001: Thread Ending Summary** workflow:

```bash
# 1. Review working notes
cat .ephemeral/sessions/current-work.md

# 2. Extract valuable information
#    - What was accomplished?
#    - What decisions were made?
#    - What was learned?
#    - What's next?

# 3. Create final summary using template
vim docs/sessions/V1x/FINAL-SUMMARY.md

# 4. Commit to git
git add docs/sessions/ && git commit -m "docs: Add V1x session summary"
```

## Template Sections

Each `FINAL-SUMMARY.md` should include:

- 🎯 What We Accomplished
- 🔑 Key Decisions
- 🧪 Testing Results
- 📚 Lessons Learned
- 🚀 Next Steps
- 📎 Related Files

See `resources/patterns/session-documentation.yaml` for the full template.

## Philosophy

This separation (ephemeral vs persistent) follows:
- **GTD**: Capture → Process → Organize
- **Zettelkasten**: Fleeting notes → Permanent notes
- **Signal vs Noise**: Only commit the signal

Most working notes are noise (scaffolding). Only valuable insights are extracted for the permanent record.

## Related Resources

- `workflow://patterns/state-management` - Where transient state lives
- `workflow://meta-workflows/MW-001` - Thread ending workflow
- `.ephemeral/README.md` - Transient state explanation