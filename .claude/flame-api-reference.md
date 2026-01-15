# Flame Python API Reference - Quick Guide

## Core Modules

### flame
Main module for accessing Flame functionality.

```python
import flame
```

### Common Objects

#### flame.batch
- `flame.batch.get_node(name)` - Get node by name
- `flame.batch.selected_nodes` - List of currently selected nodes
- `flame.batch.nodes` - All nodes in current batch

#### Compass Nodes
- `.nodes` - Child nodes within compass
- `.selected` - Boolean selection state
- `.name` - Node name

### Utilities

#### Messages
```python
flame.messages.show_in_console(message, type='info'|'error'|'warning')
```

#### Shortcuts
```python
flame.execute_shortcut(shortcut_name)
```

**Common Shortcuts:**
- `"Frame Selection in Viewport"` - Frame selected nodes
- `"Set As Next Available Context"` - Set selected node as viewing context (Meta + =)
- `"Clear All Context Views"` - Clear all viewing contexts (Shift + =)

**Viewing Context Shortcuts:**
- Up to 10 contexts can be set (numbered 1-10, where 0 = 10)
- Switch to context: `Space + [1-0]`
- Previous/Next: `Tab` / `Shift + Tab`
- Select all context nodes: `Alt + =`

**Best Practice for Deterministic Context Assignment:**
```python
# Clear all contexts first, then assign in order
flame.execute_shortcut("Clear All Context Views")
for node in nodes_to_assign:
    flame.batch.selected_nodes = [node]
    flame.execute_shortcut("Set As Next Available Context")
# Result: Contexts assigned to slots 1, 2, 3... in order
```

## Hook Entry Points

### Batch Hooks
```python
def get_batch_custom_ui_actions():
    """Called by Flame to build right-click menu in Batch"""
    return [{
        'name': 'Menu Category',
        'actions': [
            {
                'name': 'Action Name',
                'execute': lambda selection: my_function(selection)
            }
        ]
    }]
```

## To Be Expanded
This reference will grow as we work with more API features.
