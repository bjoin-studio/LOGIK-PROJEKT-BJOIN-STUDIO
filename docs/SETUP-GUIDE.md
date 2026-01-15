# BJoin Studio - LOGIK-PROJEKT Setup Guide

This guide will help you set up BJoin Studio's customized LOGIK-PROJEKT environment on macOS or Linux.

## Quick Start

```bash
# Clone the repository
git clone git@github.com:bjoin-studio/LOGIK-PROJEKT-BJOIN-STUDIO.git
cd LOGIK-PROJEKT-BJOIN-STUDIO

# Run the setup script
./install/setup-bjoin-studio.sh
```

## What Gets Installed

### 1. OCIO Color Configuration
A custom OpenColorIO configuration optimized for:
- **Working Space**: ACEScg (linear, AP1 primaries)
- **Grading Space**: ACEScct (logarithmic)
- **Output Transform**: ACES 1.0 SDR Video (Rec.709) - classic ACES look
- **HDR Ready**: Rec.2100-PQ output transform included

**Supported Camera Inputs:**
- RED (REDLog3G10 / REDWideGamutRGB)
- ARRI (LogC3, LogC4 / AWG3, AWG4)
- Sony (S-Log3 / S-Gamut3, S-Gamut3.Cine)
- Blackmagic (BMDFilm Gen5 / BMDWideGamut Gen5)

### 2. Folder Template
A streamlined 77-directory project structure including:
- `camera_originals/` - Raw camera footage
- `assets/3d/` - Alembic, USD, FBX, Blender, Houdini
- `assets/audio/` - Mix, music, voiceover, production
- `editorial/` - AAF, EDL, XML, project files
- `flame/` - Archive, iterations, setups
- `processes/` - Tracking (2D/3D), rotoscope, ML
- `utilities/luts/`, `utilities/ctf/` - Color transforms

### 3. Nuke 16.x Support
- Updated launch scripts for Nuke 16.0/16.1
- Fixed import errors in Flame terminal
- OCIO integration with Nuke

---

## Installation Options

### Option 1: System-Wide (Recommended)
Installs to `/opt/bjoin-studio/ocio/` - accessible by all users and applications.

```bash
./install/setup-bjoin-studio.sh --system
```

Requires `sudo` access.

### Option 2: User Only
Installs to `~/.config/bjoin-studio/ocio/` - no sudo required.

```bash
./install/setup-bjoin-studio.sh --user-only
```

### Check Installation Status
```bash
./install/setup-bjoin-studio.sh --check
```

### Uninstall
```bash
./install/setup-bjoin-studio.sh --uninstall
```

---

## Platform-Specific Notes

### macOS
- Tested on macOS Sonoma/Sequoia
- Uses `~/.zshrc` for environment variables
- Flame 2026 at `/opt/Autodesk/flame_2026/`
- Nuke at `/Applications/Nuke16.0v2/`

### Rocky Linux 9.5 / RHEL
- Tested on Rocky Linux 9.5
- Uses `~/.bashrc` for environment variables
- Flame 2026 at `/opt/Autodesk/flame_2026/`
- Nuke typically at `/usr/local/Nuke16.0v2/`

---

## Application Configuration

### Autodesk Flame 2026
Flame will auto-detect the `$OCIO` environment variable. To verify or manually set:

1. Launch Flame
2. Go to **Preferences** → **Color Management**
3. Verify OCIO config path shows: `/opt/bjoin-studio/ocio/config.ocio`

**Note:** Flame 2026 defaults to ACES 2.0. Our config uses ACES 1.3 with the classic ACES 1.0 SDR Video output transform for a more familiar Rec.709 look.

### Foundry Nuke 15+/16+
Nuke auto-detects `$OCIO`. To verify:

1. Launch Nuke
2. Go to **Preferences** → **Color Management**
3. Verify "OCIO Config" shows the correct path
4. Working space should be ACEScg

### DaVinci Resolve
1. Go to **Preferences** → **Color Management**
2. Set "Color science" to **ACEScct**
3. Under "ACES configuration", browse to: `/opt/bjoin-studio/ocio/config.ocio`
4. Set ACES Input Transform based on your camera
5. Set ACES Output Transform to **Rec.709**

### Blender
1. Go to **Preferences** → **Rendering**
2. Under "Color Management", set "View Transform" to **Standard**
3. Blender reads `$OCIO` automatically if set before launch

---

## Verifying the Installation

### Check Environment Variable
```bash
echo $OCIO
# Should output: /opt/bjoin-studio/ocio/config.ocio
```

### Test with ociocheck (if available)
```bash
ociocheck
```

### List Available Color Spaces
```bash
# If you have OpenColorIO tools installed:
ociobakelut --listformats
```

---

## Color Pipeline Workflow

### Recommended Workflow: R3D to Rec.709

```
Camera Original (R3D)
    ↓
REDLog3G10/REDWideGamutRGB (Input Transform)
    ↓
ACEScg (Working/Compositing Space)
    ↓
ACEScct (Grading Space)
    ↓
ACES 1.0 SDR Video (Output Transform)
    ↓
Rec.709 (Display)
```

### Color Space Reference

| Role | Color Space | Description |
|------|-------------|-------------|
| Reference | ACES2065-1 | Linear, AP0 primaries (archival) |
| Working | ACEScg | Linear, AP1 primaries (compositing) |
| Grading | ACEScct | Logarithmic, AP1 (color correction) |
| Output | Rec.709 | SDR video output |
| Output (HDR) | Rec.2100-PQ | HDR10 output |

---

## Troubleshooting

### "OCIO environment variable not found"
1. Make sure you've restarted your terminal after installation
2. Or run: `source ~/.zshrc` (macOS) or `source ~/.bashrc` (Linux)

### Flame doesn't see the OCIO config
1. Check that Flame is launched from a terminal with `$OCIO` set
2. Or launch Flame after setting the variable:
   ```bash
   export OCIO="/opt/bjoin-studio/ocio/config.ocio"
   /opt/Autodesk/flame_2026/bin/startApplication
   ```

### Colors look wrong in Resolve
1. Ensure you've set the correct Input Transform for your camera
2. Make sure Output Transform is Rec.709 (not Rec.2020)
3. Check that timeline color space is ACEScct

### Permission denied on Linux
```bash
# For system install, ensure you have sudo:
sudo ./install/setup-bjoin-studio.sh --system

# Or use user-only install:
./install/setup-bjoin-studio.sh --user-only
```

---

## File Locations

### OCIO Configuration
| Platform | System Path | User Path |
|----------|-------------|-----------|
| macOS | `/opt/bjoin-studio/ocio/config.ocio` | `~/.config/bjoin-studio/ocio/config.ocio` |
| Linux | `/opt/bjoin-studio/ocio/config.ocio` | `~/.config/bjoin-studio/ocio/config.ocio` |

### LOGIK-PROJEKT Templates
```
pref/site-prefs/custom-prefs/bjoin-studio/
├── filesystem-tree.json      # Folder structure template
├── flame-workspace.json      # Flame workspace layout
└── cf_bookmarks.json         # Flame media browser bookmarks
```

### Source OCIO Files
```
resources/ocio/
├── bjoin-studio-config.ocio  # Main custom config
└── aces-1.3/                 # Reference ACES 1.3 configs
    ├── studio-config-v2.1.0_aces-v1.3_ocio-v2.1.ocio
    └── cg-config-v2.1.0_aces-v1.3_ocio-v2.1.ocio
```

---

## Support

- **Repository**: https://github.com/bjoin-studio/LOGIK-PROJEKT-BJOIN-STUDIO
- **Branch**: bjoin-studio-dev

For issues with LOGIK-PROJEKT itself, see the upstream repository.
