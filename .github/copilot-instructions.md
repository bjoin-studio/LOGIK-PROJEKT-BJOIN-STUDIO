# GitHub Copilot Instructions for LOGIK-PROJEKT-BJOIN-STUDIO

## CRITICAL RESTRICTIONS - READ FIRST

### NEVER MODIFY THESE LOCATIONS:
- `/opt/Autodesk/` - NEVER write, symlink to, or modify ANY file here
- `/Applications/Autodesk/` - NEVER modify
- Any system Flame/Autodesk installation files

**REASON**: On 2026-01-11, a careless symlink + copy operation destroyed the user's Autodesk ACES 1.1 OCIO config, causing major Flame color pipeline failures. This required emergency restoration from the installer DMG. NEVER AGAIN.

### SAFE LOCATIONS FOR CUSTOM CONFIGS:
- `/opt/bjoin-studio/` - Custom studio configs (OK to modify)
- Project repository files - OK to modify
- User home directories - OK with permission

---

## Project Context

**Repository**: LOGIK-PROJEKT-BJOIN-STUDIO
**Branch**: bjoin-studio-dev  
**GitHub Account**: bjoin-studio (SSH key: ~/.ssh/id_ed25519_bjoin_studio)
**Purpose**: Flame project creation tool with custom templates

### Key Technologies:
- Autodesk Flame 2026.2.1
- Python 3.11 (Flame's bundled Python)
- PySide6 for UI
- OCIO 2.x for color management
- Wiretap API for Flame project creation

---

## Lessons Learned (Add to this section as we go)

### 2026-01-11: OCIO Disaster
- **Problem**: Created symlink at `/opt/bjoin-studio/ocio/config.ocio` pointing to Autodesk's ACES 1.1 config
- **Mistake**: `sudo cp` followed the symlink and OVERWROTE the original Autodesk config
- **Result**: Flame color pipeline completely broken, "Could not find source color space" errors everywhere
- **Fix**: Extracted original configs from `~/Downloads/Autodesk_Flame_2026.2.1_macOS.dmg` installer
- **Rule**: NEVER symlink to or modify `/opt/Autodesk/` - use direct file copies to `/opt/bjoin-studio/` only

### 2026-01-11: OCIO BuiltinTransform Incompatibility
- **Problem**: Standard OCIO 2.x BuiltinTransform names (like `ARRI_LOGC3_EI800_AWG_to_ACES2065-1`) don't work in Flame
- **Reason**: Flame's OCIO library doesn't include all standard BuiltinTransforms
- **Solution**: Use FileTransform with Flame's CTF files at `/opt/Autodesk/colour_mgmt/configs/legacy_configs/syncolor_ctfs/`
- **Rule**: For Flame-compatible OCIO configs, always use CTF-based transforms, not BuiltinTransform

---

## Current State

### Working:
- Flame restored to factory OCIO state
- Project creation via LOGIK-PROJEKT app
- Custom filesystem templates
- Local workstation config persistence

### In Progress:
- Custom OCIO config at `/opt/bjoin-studio/ocio/config.ocio` (untested in Flame)

### User Preferences:
- ACES 1.0 SDR output look (NOT ACES 2.0 - user explicitly hates it)
- ACEScg working space
- ACEScct grading space
- Support for RED, ARRI, Sony, Blackmagic, Canon cameras

---

## Before Making Changes

1. **Read this file first**
2. **Check `/opt/Autodesk/` restriction** - if your plan touches this, STOP and ask
3. **Test destructive operations** - use `ls` before `rm`, verify paths before `cp`
4. **No symlinks to system directories** - always use direct copies

---

## Agent Identities

For specialized assistance, see [.github/agents/](agents/README.md):
- **[Flame Specialist](agents/flame-specialist.md)**: Python API, hooks, Wiretap, batch automation
- **[LOGIK-PROJEKT Architect](agents/logik-projekt-architect.md)**: App architecture, templates, PySide6 UI
- **[OCIO Colorist](agents/ocio-colorist.md)**: Color management, ACES workflows, camera integration
- **[Integration Coordinator](agents/integration-coordinator.md)**: Cross-repo coordination, MCP tools, developer experience

These agents embody deep expertise and lessons learned. Call on them for complex tasks.

---

## How to Update This File

Add new lessons learned in the format:
```
### YYYY-MM-DD: Brief Title
- **Problem**: What went wrong
- **Mistake**: What action caused it
- **Result**: What broke
- **Fix**: How it was resolved
- **Rule**: What to do differently
```
