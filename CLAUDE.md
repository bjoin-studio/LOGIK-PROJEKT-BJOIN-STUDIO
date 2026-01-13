# AI Assistant Context - LOGIK-PROJEKT-BJOIN-STUDIO

**READ THIS FILE AT THE START OF EVERY SESSION**

## 🚨 CRITICAL RESTRICTIONS

### FORBIDDEN - NEVER MODIFY:
```
/opt/Autodesk/          ← NEVER TOUCH
/Applications/Autodesk/ ← NEVER TOUCH
```

**Why?** On 2026-01-11, modifying `/opt/Autodesk/colour_mgmt/` destroyed the Flame installation's OCIO configs and required emergency restoration. This must never happen again.

### SAFE TO MODIFY:
```
/opt/bjoin-studio/      ← Custom studio configs
~/                      ← User home (with permission)
This repository         ← Always OK
```

---

## Project Identity

| Field | Value |
|-------|-------|
| Repo | LOGIK-PROJEKT-BJOIN-STUDIO |
| Branch | bjoin-studio-dev |
| GitHub | bjoin-studio |
| SSH Key | ~/.ssh/id_ed25519_bjoin_studio |
| Flame Version | 2026.2.1 |
| Python | 3.11 (Flame bundled) |

---

## User Preferences (Remembered)

- **HATES ACES 2.0** - Always use ACES 1.0 SDR output
- **Working space**: ACEScg
- **Grading space**: ACEScct  
- **No shortcuts** - User expects thorough, correct implementations
- **Explain mistakes** - Be honest about errors, don't hide them
- **NEVER make user repeat themselves** - Save requirements to this file IMMEDIATELY

---

## Reel Configuration (bjoin-studio template)

### Desktop Reel Group: "campaign1-"
Color: (0.15, 0.15, 0.2)

| Reel Name | Color (RGB) |
|-----------|-------------|
| select-clips | 0.05, 0.15, 0.05 |
| sequences | 0.05, 0.08, 0.2 |
| reference | 0.25, 0.12, 0.04 |
| finished-selects | 0.2, 0.5, 0.15 |
| elements | 0.25, 0.18, 0.35 |
| graphics | 0.15, 0.08, 0.25 |

### Batch Group "Main Batch" - Schematic Reels
| Reel Name | Color (RGB) |
|-----------|-------------|
| camera-originals | 0.05, 0.15, 0.05 |
| precomps | 0.35, 0.3, 0.1 |
| elements | 0.15, 0.25, 0.4 |
| mattes | 0.4, 0.2, 0.05 |
| tracking | 0.12, 0.1, 0.3 |
| motion-vectors | 0.1, 0.25, 0.25 |
| graphics | 0.2, 0.1, 0.3 |
| reference | 0.25, 0.05, 0.05 |
| notes | 0.25, 0.3, 0.1 |

### Library Structure (Project_Library)
- **Editorial** folder (0.239, 0.239, 0.135) → Cuts, Ref reels
- **Plates** folder (0.057, 0.131, 0.088) → Raw, Graded reels
- **Graphics** folder (0.15, 0.08, 0.25) → Elements, Titles reels
- **Deliverables** folder (0.188, 0.023, 0.023) → Masters, Postings reels

---

## Known Technical Constraints

### Flame OCIO Compatibility
- Flame does NOT support standard OCIO BuiltinTransform names
- Must use FileTransform with CTF files from:
  `/opt/Autodesk/colour_mgmt/configs/legacy_configs/syncolor_ctfs/`
- Never symlink to Autodesk directories - always copy files

### Flame Python
- Use `/opt/Autodesk/python/2026.2.1/bin/python` for Flame scripts
- Flame terminal has specific environment requirements

---

## Session Checklist

Before executing commands:
- [ ] Does this touch `/opt/Autodesk/`? → **STOP, ASK USER**
- [ ] Am I using symlinks to system dirs? → **DON'T, USE COPIES**
- [ ] Is this a destructive operation? → **VERIFY PATHS FIRST**
- [ ] Am I learning something new? → **ADD TO LESSONS BELOW**

---

## Lessons Learned Log

### 2026-01-11: The OCIO Disaster
Symlinked custom config to Autodesk's ACES 1.1 location. `sudo cp` followed symlink and destroyed original. Required DMG extraction to restore. **NEVER SYMLINK TO /opt/Autodesk/**

### 2026-01-11: BuiltinTransform Failure  
Used standard OCIO BuiltinTransform names. Flame rejected them. Had to rebuild config using CTF FileTransforms instead.

---

## Self-Building Instructions

**AI: When you learn something important, ADD IT TO THIS FILE.**

Format:
```
### YYYY-MM-DD: Title
Brief description of lesson. **KEY RULE IN BOLD**
```

This file is your persistent memory. Use it.
