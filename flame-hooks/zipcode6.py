# Flame Python Script: Compass Navigation with Viewing Contexts
# Version: 6.0
# Adds automatic viewing context assignment per compass

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

# Define viewing contexts for each compass
# Each compass can have up to 10 contexts assigned automatically
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
    # Add more compass context mappings here:
    # "3. Beauty": [
    #     "context_node_1",
    #     "context_node_2",
    # ],
}

# Optional: Configure the shortcut command names
FRAME_SHORTCUT = "Frame Selection in Viewport"  # Try "Frame Selection" or "Frame All" if this fails
CLEAR_CONTEXTS_SHORTCUT = "Clear All Context Views"  # Shift + = equivalent
SET_CONTEXT_SHORTCUT = "Set As Next Available Context"  # Meta + = + click equivalent

# --- Core Logic ---

def set_viewing_contexts(compass_display_name):
    """
    Sets viewing contexts for the specified compass.
    Clears all existing contexts first, then assigns new ones in order (1, 2, 3...).
    """
    # Check if this compass has defined contexts
    if compass_display_name not in COMPASS_CONTEXTS:
        return  # No contexts defined for this compass, skip

    context_node_names = COMPASS_CONTEXTS[compass_display_name]

    if not context_node_names:
        return  # Empty context list, skip

    try:
        # STEP 1: Clear all existing contexts (Shift + =)
        # This ensures "Set As Next Available Context" starts from slot 1
        flame.execute_shortcut(CLEAR_CONTEXTS_SHORTCUT)

        contexts_set = []

        # STEP 2: Assign contexts in order (will be slots 1, 2, 3, 4...)
        for node_name in context_node_names:
            # Get the node
            node = flame.batch.get_node(node_name)

            if not node:
                flame.messages.show_in_console(
                    f"Context Warning: Node '{node_name}' not found. Skipping.",
                    type='warning'
                )
                continue

            # Select the node
            flame.batch.selected_nodes = [node]

            # Execute the "Set As Next Available Context" shortcut
            # Since we cleared all contexts, this assigns to 1, then 2, then 3, etc.
            flame.execute_shortcut(SET_CONTEXT_SHORTCUT)

            contexts_set.append(node_name)

        # Clear selection
        flame.batch.selected_nodes = []

        if contexts_set:
            flame.messages.show_in_console(
                f"Contexts: Set {len(contexts_set)} viewing contexts for {compass_display_name}",
                type='info'
            )

    except Exception as e:
        flame.messages.show_in_console(
            f"Context Error: Failed to set viewing contexts. {e}",
            type='error'
        )

def goto_compass(compass_display_name):
    """
    Finds a compass node by name, selects it, and frames it in the view.
    Also sets viewing contexts for the compass if defined.
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
        # Set viewing contexts FIRST (before navigation)
        set_viewing_contexts(compass_display_name)

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
