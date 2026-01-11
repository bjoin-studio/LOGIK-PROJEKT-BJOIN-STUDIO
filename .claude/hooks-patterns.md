# Flame Python Hook Patterns & Best Practices

## Hook Structure Template

### Basic Batch Right-Click Menu Hook
```python
import flame

def get_batch_custom_ui_actions():
    """Entry point for Batch context menu"""
    return [{
        'name': 'Menu Category Name',
        'actions': [
            {
                'name': 'Action Display Name',
                'execute': lambda selection: handler_function(selection)
            }
        ]
    }]
```

## Common Patterns

### 1. Node Selection & Framing
```python
# Clear and select specific node
flame.batch.selected_nodes = []
flame.batch.selected_nodes = [node]

# Execute frame command
flame.execute_shortcut("Frame Selection in Viewport")

# Clean up selection
flame.batch.selected_nodes = []
```

### 2. Finding Nodes by Name
```python
node = flame.batch.get_node("node_name")
if not node:
    flame.messages.show_in_console("Node not found", type='error')
    return
```

### 3. Validating Compass Nodes
```python
if not hasattr(node, 'nodes'):
    flame.messages.show_in_console("Not a compass node", type='error')
    return
```

### 4. Dynamic Menu Generation
```python
# Use a configuration dictionary to generate menu items
CONFIG = {
    "Display 1": "internal_name_1",
    "Display 2": "internal_name_2",
}

actions = []
for display_name in sorted(CONFIG.keys()):
    actions.append({
        'name': f'Action {display_name}',
        'execute': lambda sel, name=display_name: handler(name)
    })
```

## Error Handling
Always wrap operations in try/except and provide user feedback:
```python
try:
    # Operation
    flame.messages.show_in_console("Success message", type='info')
except Exception as e:
    flame.messages.show_in_console(f"Error: {e}", type='error')
```

## Configuration Best Practice
Keep configuration at the top of the file for easy user customization.
