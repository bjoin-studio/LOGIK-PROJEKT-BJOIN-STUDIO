# Flame Python Hooks Development - Project Context

## Environment
- **Flame Version**: 2026.1
- **Python Location**: `/opt/Autodesk/shared/python/`
- **Development Workflow**: Symbolic links from `flame-hooks/` to Flame's python directory

## Project Structure
```
LOGIK-PROJEKT-BJOIN-STUDIO/
├── flame-hooks/              # Development directory (git-tracked)
│   ├── zipcode.py           # Current: zipcode5.py, working towards zipcode6.py
│   └── ...                  # Other hooks in development
├── .claude/
│   ├── project-context.md   # This file
│   ├── flame-api-reference.md
│   ├── hooks-patterns.md
│   └── examples/            # Reference implementations
└── scripts/
    └── sync-to-flame.sh     # Symbolic link setup script
```

## Active Development

### Current Script: zipcode (Compass Navigation)

#### zipcode5.py (Production)
- **Location**: `/opt/Autodesk/shared/python/zipcode5.py`
- **Purpose**: Right-click menu for navigating between Batch compass nodes
- **Status**: Stable, in production use

#### zipcode6.py (Ready for Testing)
- **Location**: `flame-hooks/zipcode6.py` (not yet symlinked)
- **Enhancement**: Automatic viewing context assignment per compass
- **Status**: Implementation complete, ready for testing

**Viewing Context Mappings:**

**1. Prep Compass** → Contexts:
1. plate1_mux
2. plate1_denoise_mux
3. switch_undistort_mux
4. cleanEdge_mux

**2. Key Compass** → Contexts:
1. cleanEdge_mux
2. key_cleanPlate_mux

**Implementation Details:**
- Uses `flame.execute_shortcut("Set As Next Available Context")`
- Contexts set automatically before compass navigation
- User can then switch via `Space + [1-4]` for Prep, `Space + [1-2]` for Key
- See [.claude/examples/zipcode6-design.md](.claude/examples/zipcode6-design.md) for details

## Development Notes
- Hooks must physically reside in `/opt/Autodesk/shared/python/` to be loaded by Flame
- Use symbolic links to keep source in git repo while making them accessible to Flame
- Flame loads Python hooks on startup and on manual refresh
