# Flame Python Script: Compass Navigation
# Version: 2.0
# Corrected for proper compass node selection and framing

import flame

# --- Configuration ---
# Define your compass names here. The key is the menu item name,
# and the value is the exact compass node name in your Batch schematic.
# These will appear in alphabetical order in the right-click menu.
COMPASSES = {
    "1. Prep": "footage_prep",
    "2. Key": "key",
    "3. Beauty": "beauty",
    "4. Color": "color",
    "5. Linear Grade": "Linear_Grade",
    "6. Stabilize": "camera_move_stabilization",
    "7. Scale": "scale_to_formats",
    "8. Timewarp": "timewarp",
    "9. Steam": "steam_comp_full_res",
    # Add more compasses here:
    # "9. Your Compass": "your_compass_node_name",
    # "10. Another": "another_compass_name",
}

# Optional: Configure the shortcut command name if "Frame Selected" doesn't work
FRAME_SHORTCUT = "Frame Selection in Viewport"  # Try "Frame Selection" or "Frame All" if this fails

# --- Core Logic ---

def goto_compass(compass_display_name):
    """
    Finds a compass node by name, selects it, and frames it in the view.
    Uses proper selection API to ensure framing works.
    """
    if compass_display_name not in COMPASSES:
        flame.messages.show_in_console(
            f"Compass Error: '{compass_display_name}' is not defined in the script.",
            type='error'
        )
        return

    compass_node_name = COMPASSES[compass_display_name]
    compass = flame.batch.get_node(compass_node_name)

    if not compass:
        flame.messages.show_in_console(
            f"Compass Error: Node '{compass_node_name}' not found in the current Batch schematic.",
            type='error'
        )
        return

    # Verify it's actually a compass node (has .nodes attribute)
    if not hasattr(compass, 'nodes'):
        flame.messages.show_in_console(
            f"Compass Error: '{compass_node_name}' is not a compass node.",
            type='error'
        )
        return

    try:
        # CRITICAL FIX: Use flame.batch.selected_nodes instead of .selected attribute
        # This ensures proper selection state before framing
        flame.batch.selected_nodes = []  # Clear current selection
        flame.batch.selected_nodes = [compass]  # Select only the compass

        # Verify selection took effect
        if not compass.selected:
            flame.messages.show_in_console(
                f"Compass Error: Failed to select '{compass_node_name}'.",
                type='error'
            )
            return

        # Execute Flame's frame command
        flame.execute_shortcut(FRAME_SHORTCUT)

        # Deselect all nodes after framing
        flame.batch.selected_nodes = []

        flame.messages.show_in_console(
            f"Compass: Jumped to {compass_display_name} ('{compass_node_name}')",
            type='info'
        )

    except Exception as e:
        flame.messages.show_in_console(
            f"Compass Error: Could not frame compass. {e}",
            type='error'
        )

# --- Flame Menu Boilerplate ---

def get_batch_custom_ui_actions():
    """
    This function is called by Flame to build the custom right-click menu.
    It dynamically creates a menu item for each entry in the COMPASSES dictionary.
    """
    actions = []

    # Sort the keys to ensure consistent menu order (1-10 will sort correctly)
    for display_name in sorted(COMPASSES.keys()):
        actions.append({
            'name': f'Go to {display_name}',
            # Lambda with default argument captures current value correctly
            'execute': lambda selection, name=display_name: goto_compass(name)
        })

    return [{
        'name': 'Compass Navigation',
        'actions': actions
    }]
