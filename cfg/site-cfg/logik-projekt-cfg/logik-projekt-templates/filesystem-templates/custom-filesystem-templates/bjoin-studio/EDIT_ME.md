# bjoin-studio Custom Folder Template

## Instructions
1. Edit the folder structure below by creating/deleting folders in this directory
2. Or edit the `filesystem-tree-DRAFT.json` directly
3. When done, tell Claude to read this back and implement it

## Current Structure (MODIFY THIS)

Below is a SIMPLIFIED version of the default template. 
I've kept critical folders and trimmed the docs/ section significantly.

### Folders to KEEP (Critical - Don't Remove):
- flame/ (archive, iterations, setups)
- logs/
- cfg/
- backup/
- shots/
- software/

### Folders I've Simplified:
- docs/ - reduced from 20+ subcategories to just essentials
- assets/ - kept but can be customized
- editorial/ - kept core structure

### Your Workflow Additions:
Add any folders specific to your R3D/ACEScg workflow here!

---

## Quick Reference: What Each Folder Does

| Folder | Purpose | Safe to Modify? |
|--------|---------|-----------------|
| `flame/` | Flame archives, iterations, setups | ❌ NO |
| `flame/archive/` | Project archives from Flame | ❌ NO |
| `flame/iterations/` | Flame iteration saves | ❌ NO |
| `logs/` | Automation logging | ❌ NO |
| `cfg/` | Project configuration | ⚠️ Careful |
| `backup/` | Backup scripts | ⚠️ Careful |
| `shots/` | Shot-based work (created dynamically) | ✅ YES |
| `software/` | App configs, OCIO, Nuke scripts | ⚠️ Careful |
| `assets/` | Source materials | ✅ YES |
| `docs/` | Documentation | ✅ YES |
| `editorial/` | Edit files, XMLs, AAFs | ✅ YES |
| `masters/` | Final deliverables | ✅ YES |
| `reference/` | Reference materials | ✅ YES |
| `scenes/` | 3D app project files | ✅ YES |

