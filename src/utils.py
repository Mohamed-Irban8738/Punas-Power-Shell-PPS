"""
Utility functions for Punas Power Shell.
"""

from typing import Optional, Tuple


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable size."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes //= 1024
    return f"{size_bytes:.1f}PB"


def validate_filename(filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a filename.
    Returns (is_valid, error_message).
    """
    if not filename:
        return (False, "Filename cannot be empty")
    
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        if char in filename:
            return (False, f"Filename contains invalid character: {char}")
    
    if filename in [".", ".."]:
        return (False, f"'{filename}' is reserved")
    
    if filename.startswith("-"):
        return (False, "Filename cannot start with '-'")
    
    return (True, None)


def validate_path(path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a path.
    Returns (is_valid, error_message).
    """
    if not path:
        return (False, "Path cannot be empty")
    
    if path == "/" or path == ".":
        return (True, None)
    
    # For now, just check it's not empty
    # More complex validation can be added later
    return (True, None)


def normalize_path(path: str) -> str:
    """Normalize a path to use forward slashes."""
    return path.replace("\\", "/")


def parse_arguments(args_string: str) -> list[str]:
    """
    Parse a command argument string into a list.
    Handles quoted strings.
    """
    # This is a simple implementation
    # A more robust one would handle escaped quotes, etc.
    import shlex
    try:
        return shlex.split(args_string)
    except ValueError:
        # If shlex fails, return the raw string split
        return args_string.split()


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate a string to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def highlight_match(text: str, pattern: str, highlight_char: str = "*") -> str:
    """Highlight pattern matches in text."""
    if not pattern:
        return text
    
    pattern_lower = pattern.lower()
    text_lower = text.lower()
    result = []
    i = 0
    
    while i < len(text):
        if text_lower[i:i+len(pattern)].lower() == pattern_lower:
            result.append(f"{highlight_char}{text[i:i+len(pattern)]}{highlight_char}")
            i += len(pattern)
        else:
            result.append(text[i])
            i += 1
    
    return "".join(result)


def pluralize(count: int, singular: str, plural: str = None) -> str:
    """Pluralize a word based on count."""
    if plural is None:
        plural = singular + "s"
    
    return singular if count == 1 else plural


def format_timestamp(dt) -> str:
    """Format a datetime object as a readable string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: int) -> str:
    """Format duration in seconds as human readable."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
