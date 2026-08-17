"""
Command history tracking for Punas Power Shell.
"""

from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class HistoryEntry:
    """Represents a single command in history."""
    
    command: str
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    
    def __str__(self) -> str:
        time_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        status = "[OK]" if self.success else "[FAIL]"
        return f"{time_str} {status} {self.command}"


class CommandHistory:
    """Track command history with timestamps."""
    
    def __init__(self, max_size: int = 1000) -> None:
        """Initialize command history."""
        self.entries: list[HistoryEntry] = []
        self.max_size = max_size
    
    def add(self, command: str, success: bool = True) -> None:
        """Add a command to history."""
        entry = HistoryEntry(command=command, success=success)
        self.entries.append(entry)
        
        # Limit history size
        if len(self.entries) > self.max_size:
            self.entries.pop(0)
    
    def get_all(self) -> list[HistoryEntry]:
        """Get all history entries."""
        return self.entries.copy()
    
    def get_recent(self, count: int = 10) -> list[HistoryEntry]:
        """Get the most recent N entries."""
        return self.entries[-count:] if self.entries else []
    
    def search(self, pattern: str) -> list[HistoryEntry]:
        """Search history for entries containing pattern."""
        return [
            entry for entry in self.entries
            if pattern.lower() in entry.command.lower()
        ]
    
    def clear(self) -> None:
        """Clear all history."""
        self.entries.clear()
    
    def size(self) -> int:
        """Get current history size."""
        return len(self.entries)
