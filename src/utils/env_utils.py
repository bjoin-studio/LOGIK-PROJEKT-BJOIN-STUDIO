#!/usr/bin/env python3
# -------------------------------------------------------------------------- #
# Filename:     env_utils.py
# Purpose:      Utility for loading environment variables from .env file
# Description:  This module provides functions to safely load and access
#               environment variables, including API keys and configuration.

# Author:       LOGIK-PROJEKT Contributors
# Copyright:    Copyright (c) 2025
# License:      GNU General Public License v3.0 (GPL-3.0).
#               https://www.gnu.org/licenses/gpl-3.0.en.html

# Version:      1.0.0
# Status:       Production
# Type:         Utility
# Created:      2025-11-18
# -------------------------------------------------------------------------- #

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any


def find_env_file() -> Optional[Path]:
    """
    Find the .env file by searching up the directory tree.
    
    Returns:
        Path to .env file if found, None otherwise.
    """
    current_dir = Path.cwd()
    
    # Search up the directory tree for .env file
    for parent in [current_dir] + list(current_dir.parents):
        env_file = parent / '.env'
        if env_file.exists():
            return env_file
    
    return None


def load_env_file(env_path: Optional[Path] = None) -> Dict[str, str]:
    """
    Load environment variables from .env file.
    
    Args:
        env_path: Optional path to .env file. If not provided, will search for it.
        
    Returns:
        Dictionary of environment variables loaded from file.
    """
    env_vars = {}
    
    if env_path is None:
        env_path = find_env_file()
    
    if env_path is None or not env_path.exists():
        logging.debug("No .env file found")
        return env_vars
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    env_vars[key] = value
                    # Also set in os.environ for compatibility
                    os.environ[key] = value
        
        logging.info(f"Loaded {len(env_vars)} environment variables from {env_path}")
        
    except Exception as e:
        logging.error(f"Error loading .env file: {e}")
    
    return env_vars


def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get an environment variable value.
    
    Args:
        key: The environment variable name.
        default: Default value if the variable is not set.
        
    Returns:
        The environment variable value or default.
    """
    return os.environ.get(key, default)


def get_api_key(service: str) -> Optional[str]:
    """
    Get an API key for a specific service.
    
    Args:
        service: The service name (e.g., 'ANTHROPIC', 'OPENAI').
        
    Returns:
        The API key if found, None otherwise.
    """
    key_name = f"{service.upper()}_API_KEY"
    api_key = get_env_var(key_name)
    
    if not api_key or api_key == f"your-{service.lower()}-api-key-here":
        logging.warning(f"{key_name} not configured in .env file")
        return None
    
    return api_key


def is_debug_mode() -> bool:
    """
    Check if the application is running in debug mode.
    
    Returns:
        True if debug mode is enabled, False otherwise.
    """
    debug_value = get_env_var('DEBUG', 'False').lower()
    return debug_value in ('true', '1', 'yes', 'on')


def get_environment() -> str:
    """
    Get the current environment mode.
    
    Returns:
        The environment mode (development, staging, production).
    """
    return get_env_var('ENVIRONMENT', 'development')


# Auto-load environment variables when module is imported
_env_vars = load_env_file()


# Example usage
if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Load environment variables
    env_vars = load_env_file()
    
    # Example: Get Claude API key
    claude_api_key = get_api_key('anthropic')
    if claude_api_key:
        print(f"Claude API key found: {claude_api_key[:8]}...")
    else:
        print("Claude API key not configured")
    
    # Example: Check debug mode
    if is_debug_mode():
        print("Running in debug mode")
    else:
        print("Running in production mode")
    
    # Example: Get environment
    print(f"Environment: {get_environment()}")
