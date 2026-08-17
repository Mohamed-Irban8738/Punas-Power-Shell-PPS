"""
Configuration management for Punas Power Shell.
Manages settings, loads/saves from config.json.
"""

import json
import os
from typing import Any


class Config:
    """Manage shell configuration."""
    
    DEFAULT_CONFIG = {
        "theme": "default",
        "prompt_format": "psh",
        "history_size": 1000,
        "log_file": "shell.log",
        "enable_logging": True,
        "colors_enabled": False,
        "auto_cd": False,
    }
    
    def __init__(self, config_file: str = "config.json") -> None:
        """Initialize configuration."""
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            # Create default config
            self.save()
            return
        
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # Merge with defaults (don't lose new default keys)
                self.config.update(loaded)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config file: {e}")
            print("Using default configuration")
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.config[key] = value
        self.save()
    
    def get_all(self) -> dict:
        """Get all configuration values."""
        return self.config.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access."""
        return self.config[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dict-like assignment."""
        self.config[key] = value
        self.save()
    
    def __contains__(self, key: str) -> bool:
        """Allow 'in' operator."""
        return key in self.config
