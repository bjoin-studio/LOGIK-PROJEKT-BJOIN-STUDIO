# zipcode6.py Enhancement Plan

## New Feature: Viewing Contexts Per Compass

### Goal
When navigating to a compass, automatically set appropriate viewing contexts for that workflow area.

### Requirements
- **1. Prep Compass** → Set contexts:
  - plate1_mux
  - plate1_denoise_mux
  - switch_undistort_mux
  - cleanEdge_mux

- **2. Key Compass** → Set contexts:
  - cleanEdge_mux
  - key_cleanPlate_mux

### Implementation Plan

#### 1. Add Viewing Contexts Configuration
```python
VIEWING_CONTEXTS = {
    "1. Prep": ["plate1_mux", "plate1_denoise_mux", "switch_undistort_mux", "cleanEdge_mux"],
    "2. Key": ["cleanEdge_mux", "key_cleanPlate_mux"],
    # Leave empty list or omit key if no context switching needed
    "3. Beauty": [],
}
```

#### 2. Create `set_viewing_contexts()` Function
- Get current desktop via `flame.get_current_desktop()`
- Set `desktop.viewing_contexts` to the list of context names
- Handle errors gracefully
- Show console feedback

#### 3. Enhance `goto_compass()` Function
- After successful navigation and framing
- Check if compass has defined contexts in config
- If yes, call `set_viewing_contexts()`
- Maintain backward compatibility (compasses without contexts still work)

#### 4. Error Handling Considerations
- What if viewing contexts don't exist?
- What if desktop API fails?
- Should we warn user or fail silently?
- Decision: Show warning but don't block navigation

### API Research Needed
Need to verify Flame 2026.1 desktop API:
- `flame.get_current_desktop()` - correct method?
- `desktop.viewing_contexts` - correct attribute?
- Does it accept list of strings?
- Any other desktop methods we should know about?

### Testing Strategy
1. Test navigation without contexts (backward compatibility)
2. Test with valid contexts
3. Test with invalid/non-existent contexts
4. Test with empty context list
5. Verify console messages are helpful

### Version Notes
- Bump to version 3.0 (major feature addition)
- Update header with new functionality description
- Keep all v5 features intact
