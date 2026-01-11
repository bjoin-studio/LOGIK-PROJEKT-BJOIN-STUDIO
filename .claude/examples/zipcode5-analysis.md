# zipcode5.py - Compass Navigation Hook

## Purpose
Provides quick navigation between Batch compass nodes via right-click menu.

## Key Features
1. **Dynamic Menu Generation**: Creates menu items from COMPASSES dictionary
2. **Node Selection**: Properly selects compass node before framing
3. **View Framing**: Executes Flame shortcut to frame the selected compass
4. **Error Handling**: Validates node existence and type before operations

## Configuration
```python
COMPASSES = {
    "1. Prep": "footage_prep",
    "2. Key": "key",
    "3. Beauty": "beauty",
    # ... etc
}
```

## Core Function: goto_compass()
1. Validates compass exists in configuration
2. Retrieves node via `flame.batch.get_node()`
3. Validates it's actually a compass (has `.nodes` attribute)
4. Clears current selection
5. Selects target compass
6. Executes frame shortcut
7. Clears selection again
8. Shows console feedback

## Menu Structure
```
Compass Navigation
  ├── Go to 1. Prep
  ├── Go to 2. Key
  ├── Go to 3. Beauty
  └── ... (alphabetically sorted)
```

## Technical Notes
- Uses `flame.batch.selected_nodes` (not `.selected`) for proper selection
- Lambda captures display_name with default argument to avoid closure issues
- Sorted keys ensure consistent menu ordering
