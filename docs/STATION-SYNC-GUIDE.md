# LOGIK-PROJEKT Station Sync Guide

> **For AI Assistants**: Read this when picking up work on a new workstation.

---

## Quick Answer

**Switch to `bjoin-studio-dev`** — this is the active development branch across all workstations.

```bash
git stash
git checkout bjoin-studio-dev
git pull origin bjoin-studio-dev
```

---

## Branch Strategy

| Branch | Purpose | Status |
|--------|---------|--------|
| `bjoin-studio-dev` | Active development — use this | ✅ Current |
| `release-2026.2.1` | Upstream release tag | 🔒 Frozen |
| `main` | Stable releases only | 🔒 Frozen |

**All workstations should be on `bjoin-studio-dev`.**

---

## What's New (Since release-2026.2.1)

### 1. CTF Color Transform Files (52 files)
**Location**: `cfg/site-cfg/flame-cfg/flame-presets/flame_colortoolkit/`

Cameras supported:
- Apple Log
- ARRI LogC3/C4
- Canon C-Log2/3
- Sony S-Log3
- RED Log3G10
- BMD Film Gen5
- Panasonic V-Log

> **Note**: These are Flame-compatible CTF transforms, not OCIO BuiltinTransforms (Flame doesn't support those).

### 2. 789-projekt-template
**Location**: `pref/site-prefs/custom-prefs/789-projekt-template/`

Contains:
- Custom bookmarks
- Filesystem tree config
- Flame workspace config

### 3. Workspace Naming Fix
**File**: `src/core/functions/get/get_projekt_summary_data.py`

Changed to hostname-only naming (not username-hostname) because Flame runs as root, so `get_current_user()` returns "root" instead of the actual user.

### 4. Agent Identity System
**Locations**: 
- `.github/agents/`
- `CLAUDE.md`
- `.github/copilot-instructions.md`

Persistent memory system for AI assistants with lessons learned.

---

## ⚠️ CRITICAL RESTRICTIONS

### NEVER MODIFY THESE LOCATIONS

```
/opt/Autodesk/          ← NEVER TOUCH
/Applications/Autodesk/ ← NEVER TOUCH (macOS)
```

**Why?** On 2026-01-11, a symlink + copy operation destroyed Autodesk's ACES 1.1 OCIO config, breaking Flame completely. Required emergency restoration from installer DMG.

### Safe to Modify

```
/opt/bjoin-studio/      ← Custom studio configs
~/                      ← User home
This repository         ← Always OK
```

---

## User Preferences

Remember these across all sessions:

- **HATES ACES 2.0** — Always use ACES 1.0 SDR output
- **Working space**: ACEScg
- **Grading space**: ACEScct
- **Supported cameras**: RED, ARRI, Sony, Blackmagic, Canon, Panasonic, Apple

---

## Files to Ignore

These are machine-specific runtime files (regenerate on each project creation):

```
pref/session-preferences/current_session-adsk.json
pref/session-preferences/current_session-flame_launcher.sh
pref/session-preferences/current_session-variables.json
pref/session-preferences/current_session-wiretap_template.xml
```

Don't commit changes to these.

---

## Running LOGIK-PROJEKT

### Linux
```bash
cd /path/to/LOGIK-PROJEKT-BJOIN-STUDIO
/opt/Autodesk/python/2026.2.1/bin/python -m src.app
```

### macOS
```bash
cd /path/to/LOGIK-PROJEKT-BJOIN-STUDIO
/opt/Autodesk/python/2026.2.1/bin/python -m src.app
# Or use the .app bundle
```

---

## Verification After Sync

```bash
# Confirm branch
git branch --show-current
# Expected: bjoin-studio-dev

# Confirm CTFs exist
ls cfg/site-cfg/flame-cfg/flame-presets/flame_colortoolkit/ | wc -l
# Expected: 52+

# Confirm agents exist
ls .github/agents/
# Expected: flame-specialist.md, logik-projekt-architect.md, etc.
```

---

## Remote Configuration

```
origin    git@github-bjoin-studio:bjoin-studio/LOGIK-PROJEKT-BJOIN-STUDIO.git
upstream  git@github.com:flamelogik/LOGIK-PROJEKT.git
```

SSH config needed (`~/.ssh/config`):
```
Host github-bjoin-studio
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_bjoin_studio
```

---

*Last updated: 2026-02-18*
