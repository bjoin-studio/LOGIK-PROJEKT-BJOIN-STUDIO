#!/bin/bash
# Deploy Flame Python Hook via Symbolic Link
# Usage: ./deploy_hook.sh <path-to-hook.py>

set -e

FLAME_PYTHON_DIR="/opt/Autodesk/shared/python"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <hook-file.py>"
    echo "Example: $0 active/zipcode6.py"
    exit 1
fi

HOOK_FILE="$1"
HOOK_NAME=$(basename "$HOOK_FILE")

# Convert to absolute path if relative
if [[ "$HOOK_FILE" != /* ]]; then
    HOOK_FILE="$SCRIPT_DIR/$HOOK_FILE"
fi

# Check if source file exists
if [ ! -f "$HOOK_FILE" ]; then
    echo "Error: Hook file not found: $HOOK_FILE"
    exit 1
fi

# Check if Flame python directory exists
if [ ! -d "$FLAME_PYTHON_DIR" ]; then
    echo "Error: Flame python directory not found: $FLAME_PYTHON_DIR"
    echo "Is Flame installed?"
    exit 1
fi

TARGET_LINK="$FLAME_PYTHON_DIR/$HOOK_NAME"

# Remove existing file/link if it exists
if [ -e "$TARGET_LINK" ] || [ -L "$TARGET_LINK" ]; then
    echo "Removing existing: $TARGET_LINK"
    rm "$TARGET_LINK"
fi

# Create symbolic link
ln -s "$HOOK_FILE" "$TARGET_LINK"

echo "✓ Deployed: $HOOK_NAME"
echo "  Source: $HOOK_FILE"
echo "  Target: $TARGET_LINK"
echo ""
echo "Restart Flame or reload Python hooks to use the updated script."
