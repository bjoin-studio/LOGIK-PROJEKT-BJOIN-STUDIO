#!/usr/bin/env python3
# -------------------------------------------------------------------------- #
# Filename:     local_workstation_config.py
# Purpose:      Manages local workstation-specific configuration.
# Description:  Provides functions to read/write machine-specific settings
#               that persist per workstation but are not tracked in git.

# Author:       bjoin-studio
# Copyright:    Copyright (c) 2025
# License:      GNU General Public License v3.0 (GPL-3.0).

# Version:      2026.2.1
# Status:       Production
# Created:      2026-01-11
# -------------------------------------------------------------------------- #

import json
import os
from pathlib import Path
from typing import Optional, Any


def get_local_config_path() -> Path:
    """
    Get the path to the local workstation config file.
    
    The file is stored in the repo root as local_workstation.json
    and is gitignored so each machine can have its own settings.
    
    Returns:
        Path to local_workstation.json
    """
    # Find the repo root (where .git folder is)
    current = Path(__file__).resolve()
    
    # Navigate up to find repo root (src/core/utils -> repo root)
    repo_root = current.parent.parent.parent.parent
    
    return repo_root / "local_workstation.json"


def load_local_config() -> dict:
    """
    Load the local workstation configuration.
    
    Returns:
        Dictionary of local settings, or empty dict if file doesn't exist
    """
    config_path = get_local_config_path()
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load local_workstation.json: {e}")
        return {}


def save_local_config(config: dict) -> bool:
    """
    Save the local workstation configuration.
    
    Args:
        config: Dictionary of settings to save
        
    Returns:
        True if successful, False otherwise
    """
    config_path = get_local_config_path()
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except IOError as e:
        print(f"Error: Could not save local_workstation.json: {e}")
        return False


def get_local_setting(key: str, default: Any = None) -> Any:
    """
    Get a specific setting from local workstation config.
    
    Args:
        key: The setting key to retrieve
        default: Default value if key not found
        
    Returns:
        The setting value or default
    """
    config = load_local_config()
    return config.get(key, default)


def set_local_setting(key: str, value: Any) -> bool:
    """
    Set a specific setting in local workstation config.
    
    Args:
        key: The setting key to set
        value: The value to store
        
    Returns:
        True if successful, False otherwise
    """
    config = load_local_config()
    config[key] = value
    return save_local_config(config)


# Convenience functions for common settings
def get_local_flame_home_dir() -> Optional[str]:
    """Get the locally configured Flame home directory."""
    return get_local_setting("flame_home_dir")


def set_local_flame_home_dir(path: str) -> bool:
    """Set the local Flame home directory."""
    return set_local_setting("flame_home_dir", path)


def get_local_flame_setups_dir() -> Optional[str]:
    """Get the locally configured Flame setups directory."""
    return get_local_setting("flame_setups_dir")


def set_local_flame_setups_dir(path: str) -> bool:
    """Set the local Flame setups directory."""
    return set_local_setting("flame_setups_dir", path)


def get_local_flame_media_dir() -> Optional[str]:
    """Get the locally configured Flame media directory."""
    return get_local_setting("flame_media_dir")


def set_local_flame_media_dir(path: str) -> bool:
    """Set the local Flame media directory."""
    return set_local_setting("flame_media_dir", path)
