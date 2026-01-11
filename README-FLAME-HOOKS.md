# Flame Python Hooks Development

Development environment for Autodesk Flame 2026.1 Python hooks with Claude Code.

## Structure

```
LOGIK-PROJEKT-BJOIN-STUDIO/
├── flame-hooks/              # Development directory (edit here!)
│   └── zipcode5.py          # Compass navigation hook
├── .claude/                  # Claude Code knowledge base
│   ├── project-context.md   # Project setup & active work
│   ├── flame-api-reference.md
│   ├── hooks-patterns.md
│   └── examples/
├── scripts/
│   └── sync-to-flame.sh     # Symlink script
└── README-FLAME-HOOKS.md    # This file
```

## Workflow

### 1. Develop in `flame-hooks/`
Edit your Python hooks in the [flame-hooks/](flame-hooks/) directory. This is git-tracked.

### 2. Sync to Flame
Run the sync script to create symbolic links:
```bash
./scripts/sync-to-flame.sh
```

This creates symlinks from `/opt/Autodesk/shared/python/` to your development files.

### 3. Test in Flame
- Restart Flame, OR
- Use Flame's "Refresh Python Hooks" command (if available)

### 4. Iterate
Changes to files in `flame-hooks/` are immediately reflected in Flame (via symlinks).

## Current Hooks

### zipcode5.py - Compass Navigation
Right-click menu for jumping between Batch compass nodes.
- **Status**: Production
- **Documentation**: [.claude/examples/zipcode5-analysis.md](.claude/examples/zipcode5-analysis.md)

## Claude Code Integration

The `.claude/` directory contains:
- **project-context.md**: Current work, environment setup, active features
- **flame-api-reference.md**: Flame Python API quick reference
- **hooks-patterns.md**: Common patterns and best practices
- **examples/**: Detailed analysis of existing hooks

Update these as you learn new Flame API features!

## Next Steps

See [.claude/project-context.md](.claude/project-context.md) for current development tasks.
