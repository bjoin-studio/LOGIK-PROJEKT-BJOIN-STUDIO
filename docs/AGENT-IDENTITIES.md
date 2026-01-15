# Agent Identities & Repository Integration Plan

**Created**: 2026-01-14  
**Purpose**: Strategic overview of agent identity system and cross-repository coordination

---

## Executive Summary

This document outlines the **Agent Identity System** for LOGIK-PROJEKT-BJOIN-STUDIO and its integration with related repositories (nbjoin-pythonDev, vfx-agentic-research). Agent identities are structured knowledge documents that define specialized AI assistant roles, capturing:

1. **Domain Expertise**: Deep technical knowledge in specific areas
2. **Lessons Learned**: Context from production incidents and debugging sessions
3. **Integration Patterns**: How different components work together
4. **Emergency Protocols**: Troubleshooting workflows for common failures

---

## Repository Ecosystem

### Three Core Repositories

#### LOGIK-PROJEKT-BJOIN-STUDIO (This Repo)
- **Location**: `~/Documents/workspace/GitHub/bjoin-studio/LOGIK-PROJEKT-BJOIN-STUDIO`
- **Purpose**: Flame project creation toolkit with custom templates
- **Branch**: `bjoin-studio-dev` (active development)
- **GitHub**: bjoin-studio account
- **Key Features**:
  - PySide6 GUI for projekt creation
  - 77-directory filesystem templates
  - Flame workspace automation (DREAMS library structure)
  - Wiretap API integration
  - OCIO configuration management

#### nbjoin-pythonDev
- **Location**: `~/Documents/workspace/GitHub/nbjoin/nbjoin-pythonDev`
- **Purpose**: Flame/Nuke hook development sandbox
- **GitHub**: nbjoin (personal)
- **Key Features**:
  - Active Flame hooks (zipcode.py compass navigation)
  - Extensive Flame API documentation (`.claude/flame-python-api-comprehensive.md`)
  - MCP tool integration (flameKB, syntheyesKB)
  - Example batch setups and workflows

#### vfx-agentic-research
- **Location**: `~/Documents/workspace/GitHub/nbjoin/vfx-agentic-research`
- **Purpose**: MCP server development for AI-assisted VFX workflows
- **GitHub**: nbjoin (research)
- **Key MCP Servers**:
  - `flame-kb-mcp-server` - Flame documentation semantic search
  - `flame-hooks-mcp-server` - Hook code pattern search
  - `syntheyes-kb-mcp-server` - SynthEyes manual search
  - `n8n-kb-mcp-server` - Workflow automation docs

---

## Agent Identity System

### Four Specialized Agents

Located in [.github/agents/](.github/agents/README.md):

#### 1. Flame Specialist 🔥
**Domain**: Autodesk Flame Python API, hooks, Wiretap, batch automation

**Key Expertise**:
- PyNode & PyAttribute manipulation (keyframe prevention)
- Hook lifecycle (`app_initialized`, `batch_setup`, `project_saved`)
- Workspace configuration (desktop reels, batch groups, library structure)
- Wiretap project creation and XML templates
- Integration with nick-pythonDev hook patterns

**Critical Lessons**:
- Setting `PyAttribute.mode = 'constant'` prevents unwanted keyframes
- Node color attributes vary by type (`.colour` vs `.schematic_colour`)
- Batch group `reels=` parameter creates schematic reels
- RED colorspace naming mismatches require alias colorspaces

**File**: [agents/flame-specialist.md](.github/agents/flame-specialist.md)

#### 2. LOGIK-PROJEKT Architect 🏗️
**Domain**: Application architecture, filesystem templates, PySide6 UI, configuration management

**Key Expertise**:
- PySide6 application design (signals/slots, QThread workers)
- Filesystem template system (recursive JSON processing)
- Configuration layering (local → site → default)
- Template import/export workflows
- Application logging and error handling

**Critical Lessons**:
- Always initialize widgets BEFORE connecting signals
- Use QThread + Worker pattern for long-running operations
- Validate inputs BEFORE starting projekt creation
- Filesystem templates must balance organization with flexibility

**File**: [agents/logik-projekt-architect.md](.github/agents/logik-projekt-architect.md)

#### 3. OCIO Colorist 🎨
**Domain**: Color management, OpenColorIO configs, ACES workflows, camera integration

**Key Expertise**:
- OCIO 2.x config design for Flame compatibility
- ACES 1.x workflows (user HATES ACES 2.0 SDR output!)
- Camera colorspace integration (RED, ARRI, Sony, Blackmagic, Canon)
- FileTransform (CTF) vs BuiltinTransform patterns
- Color pipeline troubleshooting

**Critical Lessons** (2026-01-11 OCIO Disaster):
- **NEVER MODIFY `/opt/Autodesk/` DIRECTLY** - symlink catastrophe destroyed Flame's OCIO configs
- Flame requires FileTransform with CTF files, NOT BuiltinTransform
- Always backup Autodesk configs before modifications
- Colorspace naming mismatches require alias colorspace entries

**File**: [agents/ocio-colorist.md](.github/agents/ocio-colorist.md)

#### 4. Integration Coordinator 🔗
**Domain**: Cross-repository coordination, MCP tool orchestration, developer experience, workflow optimization

**Key Expertise**:
- Coordinating work between LOGIK-PROJEKT ↔ nbjoin-pythonDev ↔ vfx-agentic-research
- MCP server configuration and usage (flameKB, flame-hooks-mcp-server, etc.)
- Shared component organization (hooks, documentation, configs)
- Developer experience improvements (shell aliases, testing scripts, CI/CD)
- Knowledge transfer between repositories

**Critical Lessons**:
- Symlinks don't work for cross-machine collaboration (use file copying)
- Hook development workflow: sandbox (nbjoin-pythonDev) → production (LOGIK-PROJEKT)
- MCP tools provide semantic search for documentation and code examples
- Version synchronization across repos prevents divergence

**File**: [agents/integration-coordinator.md](.github/agents/integration-coordinator.md)

---

## Integration Strategy (Awaiting Approval)

### Current State: Separate Repos
- LOGIK-PROJEKT and nbjoin-pythonDev maintain independent development
- Some duplication: Flame hooks, API documentation, OCIO configs
- Manual synchronization when patterns stabilize

### Proposed Coordination (Phase 1: Documentation)
**Status**: Ready to implement, awaiting user approval

1. **Copy Flame API Reference**:
   ```bash
   mkdir -p docs/flame-api/
   cp ~/Documents/workspace/GitHub/nbjoin/nbjoin-pythonDev/.claude/flame-python-api-comprehensive.md \
      docs/flame-api/api-reference.md
   ```

2. **Add MCP Configuration**:
   ```bash
   cp ~/Documents/workspace/GitHub/nbjoin/nbjoin-pythonDev/mcp.json \
      .mcp.json
   # Edit to use workspace-relative paths
   ```

3. **Document Hook Coordination**:
   - Create `flame-hooks/COORDINATION.md` explaining how hooks move from nbjoin-pythonDev to production
   - Update both repos' READMEs with cross-references

4. **Update Setup Guide**:
   - Add MCP tool setup instructions to `docs/SETUP-GUIDE.md`
   - Document nick-pythonDev as "sister repository" with link

### Future Options (Needs Discussion)

#### Option A: Git Submodules
Add nbjoin-pythonDev as submodule in LOGIK-PROJEKT
- **Pros**: Version-locked, single clone gets both
- **Cons**: Submodules confusing, nested .git issues

#### Option B: Monorepo
Merge both into unified VFX development monorepo
- **Pros**: Single source of truth, shared CI/CD
- **Cons**: Massive restructuring, breaks existing forks

#### Option C: Symlink Coordination (Current)
Keep separate, use symlinks for shared components
- **Pros**: No restructuring, maintains independence
- **Cons**: Symlinks don't work cross-machine

#### Option D: Shared Library Package
Extract shared code into pip-installable package
- **Pros**: Professional distribution, versioned releases
- **Cons**: Packaging overhead, overkill for single developer

**Recommendation**: Start with **Phase 1** (documentation integration), then evaluate based on pain points.

---

## MCP Tool Integration

### Available MCP Servers

#### flameKB (Flame 2026 Documentation)
```python
search_flame_docs(question="How to create batch groups with Python?")
get_flame_workflow(task="stabilizing and tracking a shot")
search_flame_api(question="PyAttribute animation mode")
```

#### flame-hooks-mcp-server (Hook Code Examples)
```python
search_hooks(query="compass navigation right-click menu", limit=5)
get_hook_code(hook_path="zipcode6.py")
list_patterns(pattern="batch_setup")
```

#### syntheyesKB (SynthEyes Manual)
```python
search_syntheyes_docs(question="How to export camera data to Flame?")
get_syntheyes_workflow(task="camera solve workflow")
```

### Configuration Template
Save as `.mcp.json` in repository root:
```json
{
  "servers": {
    "flameKB": {
      "type": "stdio",
      "command": "node",
      "args": [
        "/Users/nbjoin/Documents/workspace/GitHub/nbjoin/vfx-agentic-research/02-systems/flame-kb-mcp-server/index.js"
      ]
    },
    "flame-hooks": {
      "type": "stdio",
      "command": "node",
      "args": [
        "/Users/nbjoin/Documents/workspace/GitHub/nbjoin/vfx-agentic-research/02-systems/flame-hooks-mcp-server/index.js"
      ]
    },
    "syntheyesKB": {
      "type": "stdio",
      "command": "node",
      "args": [
        "/Users/nbjoin/Documents/workspace/GitHub/nbjoin/vfx-agentic-research/02-systems/syntheyes-kb-mcp-server/index.js"
      ]
    }
  }
}
```

---

## Critical Restrictions

### FROM OCIO DISASTER (2026-01-11)

**NEVER MODIFY THESE LOCATIONS**:
- `/opt/Autodesk/` - System Flame installation
- `/Applications/Autodesk/` - Application bundle
- Any Flame/Autodesk installation files

**WHAT HAPPENED**:
1. Created symlink: `/opt/bjoin-studio/ocio/config.ocio` → `/opt/Autodesk/.../config.ocio`
2. Ran `sudo cp /opt/bjoin-studio/ocio/config.ocio /tmp/backup.ocio`
3. `cp` followed symlink and **OVERWROTE** original Autodesk config
4. Flame color pipeline completely broken
5. Required emergency restoration from installer DMG

**THE RULE**:
```bash
# FORBIDDEN:
ln -s /opt/Autodesk/anything /opt/bjoin-studio/
sudo cp /opt/bjoin-studio/symlinked-file /anywhere  # ← DISASTER!

# CORRECT:
sudo cp /opt/Autodesk/colour_mgmt/.../config.ocio /opt/bjoin-studio/ocio/aces-1.1-base.ocio
# Now edit /opt/bjoin-studio/ocio/aces-1.1-base.ocio safely
```

**SAFE LOCATIONS**:
- `/opt/bjoin-studio/` - Custom studio configs
- This repository - Version controlled
- User home (`~/`) - With permission

---

## Developer Experience Improvements

### Shell Aliases (Add to `~/.zshrc`)
```bash
# Repository navigation
alias logik='cd ~/Documents/workspace/GitHub/bjoin-studio/LOGIK-PROJEKT-BJOIN-STUDIO'
alias nickpy='cd ~/Documents/workspace/GitHub/nbjoin/nbjoin-pythonDev'
alias vfxai='cd ~/Documents/workspace/GitHub/nbjoin/vfx-agentic-research'

# Quick file access
alias flame-api='code ~/Documents/workspace/GitHub/nbjoin/nbjoin-pythonDev/.claude/flame-python-api-comprehensive.md'
alias logik-agents='code ~/Documents/workspace/GitHub/bjoin-studio/LOGIK-PROJEKT-BJOIN-STUDIO/.github/agents/'
alias ocio-backup='sudo cp -r /opt/Autodesk/colour_mgmt/configs/ /opt/bjoin-studio/backups/autodesk-configs-$(date +%Y%m%d)/'
```

### Testing Scripts (Future)
Create `scripts/test-all.sh`:
```bash
#!/bin/bash
# Validate Flame hooks
for hook in flame-hooks/*.py; do
    /opt/Autodesk/python/2026.2.1/bin/python3 -m py_compile "$hook"
done

# Validate JSON templates
for template in cfg/**/*.json; do
    python3 -m json.tool "$template" > /dev/null
done

# Validate OCIO configs
for config in resources/ocio/*.ocio; do
    /opt/Autodesk/python/2026.2.1/bin/python3 -c "
import PyOpenColorIO as ocio
ocio.Config.CreateFromFile('$config')
print('✓ $config valid')
"
done
```

---

## Usage Examples

### Example 1: "My Flame hooks aren't loading"
**Agent**: Flame Specialist

**Troubleshooting Steps**:
1. Check symlink targets: `ls -la /opt/Autodesk/shared/python/`
2. Validate Python syntax: `/opt/Autodesk/python/2026.2.1/bin/python3 -m py_compile hook.py`
3. Review Flame console output (launch with `--log-to-console`)
4. Check for duplicate module names in subdirectories
5. Verify hook file permissions (must be readable by Flame user)

### Example 2: "Need to add Canon CLog3 to OCIO config"
**Agents**: OCIO Colorist + Flame Specialist + Integration Coordinator

**Workflow**:
1. **OCIO Colorist**: Check if Autodesk has CTF transform in `/opt/Autodesk/.../syncolor_ctfs/camera/Canon/`
2. **OCIO Colorist**: Design colorspace entry with FileTransform
3. **OCIO Colorist**: Add to `/opt/bjoin-studio/ocio/bjoin-studio-config.ocio`
4. **OCIO Colorist**: Validate with PyOpenColorIO
5. **Flame Specialist**: Test clip import in Flame, verify auto-detection
6. **Flame Specialist**: Update flame-workspace.json camera presets
7. **Integration Coordinator**: Document in both LOGIK-PROJEKT and nbjoin-pythonDev

### Example 3: "App freezes during project creation"
**Agent**: LOGIK-PROJEKT Architect

**Troubleshooting Steps**:
1. Check if long operation is on main thread (should use QThread + Worker)
2. Review session log: `logs/session-logs/YYYY/MM/DD/HH-MM-SS.log`
3. Add progress signals to Worker class for UI updates
4. Verify `/PROJEKTS` mount point is accessible (may have disconnected)
5. Check disk space on target volume

---

## Knowledge Maintenance

### When to Update Agent Identities

1. **New Patterns Discovered**: Add to agent's "Core Expertise"
2. **Production Incidents**: Add to "Lessons Learned" with date
3. **Configuration Changes**: Update "Current State Awareness"
4. **Integration Changes**: Update "Integration Points"
5. **User Preferences**: Update relevant agent (e.g., color preferences → OCIO Colorist)

### Update Template
```markdown
### YYYY-MM-DD: Descriptive Title
- **Problem**: What went wrong or what was needed
- **Context**: Where it occurred, what was attempted
- **Solution**: How it was resolved or implemented
- **Lesson**: What to remember for future work
- **Rule**: Clear guideline to prevent recurrence
```

### Commit Message Format
```
[Agent] Added lesson: PyAttribute mode='constant' prevents keyframes

Documents the critical pattern discovered during batch group reel creation
debugging. This prevents unwanted keyframe creation when setting attribute
values programmatically.
```

---

## Next Steps

### Immediate (Awaiting User Approval)
1. **Copy Flame API docs** from nbjoin-pythonDev to `docs/flame-api/`
2. **Create `.mcp.json`** with flameKB, flame-hooks-mcp-server, syntheyesKB
3. **Document hook coordination** workflow in `flame-hooks/COORDINATION.md`
4. **Update READMEs** with cross-repo references

### Short-Term (After Initial Integration)
1. Test end-to-end projekt creation with new LC-26_671 project
2. Validate launcher script execution (`flame_launcher.sh` with workspace creation)
3. Add shell aliases to `~/.zshrc` for quick navigation
4. Create `scripts/test-all.sh` for pre-commit validation

### Long-Term (Strategic Planning)
1. Evaluate integration approach based on pain points
2. Consider shared library package if duplication becomes problematic
3. Plan multi-DCC workflows (Flame + Nuke + Resolve coordination)
4. Establish CI/CD for automated testing

---

## Questions & Discussion

### Open Questions
1. **Integration Approach**: Which option (A/B/C/D) for long-term repo coordination?
2. **Hook Versioning**: Semantic versioning vs suffix-based (zipcode-v6.0)?
3. **MCP Tool Expansion**: Which other MCP servers would be valuable?
4. **Testing Strategy**: Manual testing sufficient or need automated CI?

### Areas for Discussion
- Monorepo feasibility given GitHub account split (bjoin-studio vs nbjoin)
- Hook deployment workflow (manual copy vs automated sync)
- OCIO config distribution (per-project vs shared studio config)
- Documentation hosting (GitHub wiki, ReadTheDocs, local Markdown)

---

## Conclusion

The Agent Identity System provides:
- **Structured Knowledge**: Lessons learned captured in accessible format
- **Specialized Expertise**: Domain-specific agents for complex tasks
- **Integration Coordination**: Cross-repo patterns without disruption
- **Developer Experience**: Improved navigation, testing, documentation

**Philosophy**: "Every mistake strengthens the agents. Every agent empowers the developer."

---

**Status**: ✅ Agent Identities Created (2026-01-14)  
**Next Action**: User review and approval for Phase 1 integration steps  
**Maintainer**: Nick / GitHub: bjoin-studio, nbjoin
