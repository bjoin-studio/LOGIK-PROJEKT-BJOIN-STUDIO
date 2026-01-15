# zipcode6.py - Compass Navigation with Viewing Contexts

## New Features (vs zipcode5)

Automatically sets viewing contexts when navigating to a compass.

## Configuration

### Compass-to-Context Mapping
```python
COMPASS_CONTEXTS = {
    "1. Prep": [
        "plate1_mux",
        "plate1_denoise_mux",
        "switch_undistort_mux",
        "cleanEdge_mux",
    ],
    "2. Key": [
        "cleanEdge_mux",
        "key_cleanPlate_mux",
    ],
}
```

## How It Works

### Workflow
1. User selects "Go to 1. Prep" from right-click menu
2. Script calls `set_viewing_contexts("1. Prep")`
3. Script executes `flame.execute_shortcut("Clear All Context Views")` (Shift + =)
4. For each context node in the list:
   - Get node via `flame.batch.get_node(node_name)`
   - Select it via `flame.batch.selected_nodes = [node]`
   - Execute `flame.execute_shortcut("Set As Next Available Context")`
5. Script then navigates to and frames the compass (same as zipcode5)

### Context Assignment (Deterministic)
By clearing all contexts FIRST, "Set As Next Available Context" becomes deterministic:
- Context 1: plate1_mux (first in list → first available slot = 1)
- Context 2: plate1_denoise_mux (second in list → next available slot = 2)
- Context 3: switch_undistort_mux (third in list → next available slot = 3)
- Context 4: cleanEdge_mux (fourth in list → next available slot = 4)

This ensures consistent, predictable context assignments every time.

### Switching Between Contexts
Once set, users can switch via keyboard:
- `Space + 1` → View context 1 (plate1_mux)
- `Space + 2` → View context 2 (plate1_denoise_mux)
- `Tab` → Previous context
- `Shift + Tab` → Next context

## Implementation Strategy

Uses `flame.execute_shortcut()` approach rather than direct API:
- **Advantage**: Leverages Flame's built-in context system
- **Key Insight**: Clear contexts first (Shift + =) to make "Set As Next Available Context" deterministic
- **Result**: Consistent context slot assignments (1, 2, 3...) every time

## Error Handling
- Warns if context node not found, but continues with remaining contexts
- Reports how many contexts were successfully set

## Technical Notes
- Maximum 10 contexts per compass (Flame limitation)
- Contexts set BEFORE navigation to ensure they're ready when user arrives
- Shortcut name configurable via `SET_CONTEXT_SHORTCUT` constant
