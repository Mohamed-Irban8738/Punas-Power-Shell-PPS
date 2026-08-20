"""
Logging system for Punas Power Shell.
Logs commands, filesystem operations, and errors.
"""

import os
from datetime import datetime
from typing import Optional


class Logger:
    """Log commands and activities to a file."""
    
    def __init__(self, log_file: str = "shell.log") -> None:
        """Initialize logger."""
        self.log_file = log_file
        self.enabled = True
    
    def _write_log(self, level: str, message: str) -> None:
        """Write a log entry."""
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level:8} | {message}\n"
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except IOError as e:
            print(f"Warning: Could not write to log file: {e}")
    
    def info(self, message: str) -> None:
        """Log an info message."""
        self._write_log("INFO", message)
    
    def command(self, cmd: str, success: bool = True) -> None:
        """Log a command execution."""
        status = "SUCCESS" if success else "FAILED"
        self._write_log("COMMAND", f"[{status}] {cmd}")
    
    def file_created(self, filename: str, location: str = "/") -> None:
        """Log file creation."""
        self._write_log("FILESYSTEM", f"Created file: {location}/{filename}")
    
    def file_deleted(self, filename: str, location: str = "/") -> None:
        """Log file deletion."""
        self._write_log("FILESYSTEM", f"Deleted file: {location}/{filename}")
    
    def file_modified(self, filename: str, location: str = "/") -> None:
        """Log file modification."""
        self._write_log("FILESYSTEM", f"Modified file: {location}/{filename}")
    
    def directory_created(self, dirname: str, location: str = "/") -> None:
        """Log directory creation."""
        self._write_log("FILESYSTEM", f"Created directory: {location}/{dirname}")
    
    def directory_deleted(self, dirname: str, location: str = "/") -> None:
        """Log directory deletion."""
        self._write_log("FILESYSTEM", f"Deleted directory: {location}/{dirname}")
    
    def directory_changed(self, path: str) -> None:
        """Log directory change."""
        self._write_log("FILESYSTEM", f"Changed directory to: {path}")
    
    def error(self, message: str) -> None:
        """Log an error message."""
        self._write_log("ERROR", message)
    
    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._write_log("WARNING", message)
    
    def session_start(self) -> None:
        """Log session start."""
        self._write_log("SESSION", "Shell session started")
    
    def session_end(self) -> None:
        """Log session end."""
        self._write_log("SESSION", "Shell session ended")
    
    def clear_log(self) -> None:
        """Clear the log file."""
        try:
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
                self.info("Log file cleared")
        except IOError as e:
            print(f"Warning: Could not clear log file: {e}")
    
    def disable(self) -> None:
        """Disable logging."""
        self.enabled = False
    
    def enable(self) -> None:
        """Enable logging."""
        self.enabled = True
