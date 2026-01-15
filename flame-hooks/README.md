# Flame Python Hooks Development

This directory contains Python hooks for Autodesk Flame 2026.1.

## Directory Structure
```
flame-hooks/
├── active/          # Hooks currently deployed to Flame (symlinked)
├── archive/         # Older versions and deprecated hooks
└── dev/             # Work-in-progress hooks
```

## Deployment
Hooks are developed here and symlinked to `/opt/Autodesk/shared/python/` where Flame can execute them.

Use the `deploy_hook.sh` script to create/update symbolic links:
```bash
./deploy_hook.sh active/zipcode6.py
```

## Active Hooks

### zipcode (Compass Navigation)
- **Current**: zipcode5.py
- **In Development**: zipcode6.py (adding viewing contexts)
- **Purpose**: Quick navigation to compass nodes in Batch schematics

## Development Workflow
1. Create/edit hooks in appropriate subdirectory
2. Test by deploying symlink to Flame python directory
3. Iterate and test in Flame
4. Move to `active/` when ready for production use
5. Archive old versions in `archive/`

## Testing
- Restart Flame or reload Python hooks after changes
- Check Flame console for error messages
- Use `flame.messages.show_in_console()` for debugging
