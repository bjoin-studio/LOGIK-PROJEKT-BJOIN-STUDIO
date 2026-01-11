#!/bin/bash
# Symbolic Link Sync Script for Flame Python Hooks
# Syncs hooks from development directory to Flame's python folder

FLAME_PYTHON_DIR="/opt/Autodesk/shared/python"
DEV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/flame-hooks"

echo "Flame Python Hook Sync"
echo "======================"
echo "Development: $DEV_DIR"
echo "Flame Dir:   $FLAME_PYTHON_DIR"
echo ""

# Check if Flame directory exists
if [ ! -d "$FLAME_PYTHON_DIR" ]; then
    echo "ERROR: Flame python directory not found: $FLAME_PYTHON_DIR"
    exit 1
fi

# Check if dev directory exists
if [ ! -d "$DEV_DIR" ]; then
    echo "ERROR: Development directory not found: $DEV_DIR"
    exit 1
fi

# Function to create symlink
create_link() {
    local filename=$1
    local source="$DEV_DIR/$filename"
    local target="$FLAME_PYTHON_DIR/$filename"
    
    if [ ! -f "$source" ]; then
        echo "SKIP: $filename (source not found)"
        return
    fi
    
    # Remove existing file/link if it exists
    if [ -e "$target" ] || [ -L "$target" ]; then
        echo "REMOVE: Existing $filename"
        rm "$target"
    fi
    
    # Create symbolic link
    ln -s "$source" "$target"
    echo "LINK: $filename -> Flame"
}

# Sync all .py files from flame-hooks/
for pyfile in "$DEV_DIR"/*.py; do
    if [ -f "$pyfile" ]; then
        filename=$(basename "$pyfile")
        create_link "$filename"
    fi
done

echo ""
echo "Sync complete! Restart Flame or refresh Python hooks to load changes."
