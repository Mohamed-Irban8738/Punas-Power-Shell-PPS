# Punas Power Shell - API Documentation

Complete API reference for developers working with Punas Power Shell.

## Core Classes

### `PunasShell` (src/shell.py)

Main shell engine that coordinates all shell operations.

**Attributes**:
- `VERSION` (str): Shell version "1.0.0"
- `PROMPT` (str): Default prompt "psh> "
- `running` (bool): Current shell state
- `parser` (CommandParser): Command parser instance
- `dispatcher` (CommandDispatcher): Command router
- `file_manager` (FileManager): Filesystem operations
- `history` (CommandHistory): Command history tracker
- `config` (Config): Configuration manager
- `logger` (Logger): Activity logger

**Key Methods**:

#### `start()`
Start the interactive shell with banner display.
```python
shell = PunasShell()
shell.start()  # Displays banner and enters interactive mode
```

#### `run()`
Main shell loop. Continuously reads and processes commands.
```python
# Called by start(), can also be called directly
shell.run()
```

#### `process_input(command_line: str) -> None`
Parse and execute a single command line.
```python
shell.process_input("mkdir projects")
shell.process_input("cd projects")
shell.process_input("ls")
```

#### `stop()`
Gracefully stop the shell.
```python
shell.stop()  # Closes shell and logs session end
```

#### `get_prompt() -> str`
Get the current prompt based on working directory.
```python
prompt = shell.get_prompt()  # Returns "psh> " or "psh\path> "
```

---

### `VirtualFileSystem` (src/virtual_fs.py)

In-memory filesystem that isolates all file operations from the real filesystem.

**Attributes**:
- `root` (VirtualDirectory): Root directory node
- `current_directory` (VirtualDirectory): Current working directory

**Key Methods**:

#### `pwd() -> str`
Get the current working directory path.
```python
vfs = VirtualFileSystem()
cwd = vfs.pwd()  # Returns "/"
```

#### `cd(path: str) -> tuple[bool, str]`
Change current directory.
```python
success, error = vfs.cd("projects")
if success:
    print(f"Now in {vfs.pwd()}")
else:
    print(f"Error: {error}")
```

#### `ls() -> list[tuple[str, str]]`
List directory contents.
```python
items = vfs.ls()  # Returns [("dir1", "dir"), ("file.txt", "file")]
```

#### `mkdir(name: str) -> tuple[bool, str]`
Create a directory.
```python
success, msg = vfs.mkdir("newdir")
# Returns (True, "Directory created: newdir")
```

#### `touch(filename: str) -> tuple[bool, str]`
Create a file or update its timestamp.
```python
success, msg = vfs.touch("file.txt")
# Returns (True, "File created: file.txt")
```

#### `cat(filename: str) -> tuple[bool, str]`
Read file contents.
```python
success, content = vfs.cat("file.txt")
if success:
    print(content)
else:
    print(f"Error: {content}")
```

#### `echo(content: str, filename: str = None) -> tuple[bool, str]`
Write to file or return content to print.
```python
# Print to console
success, output = vfs.echo("Hello World", None)
# Returns (True, "Hello World")

# Write to file
success, msg = vfs.echo("Hello World", "greeting.txt")
# Returns (True, "Written to greeting.txt")
```

#### `cp(source: str, dest: str, recursive: bool = False) -> tuple[bool, str]`
Copy a file or directory.
```python
success, msg = vfs.cp("file.txt", "backup.txt")
# Returns (True, "File copied: file.txt -> backup.txt")

success, msg = vfs.cp("src", "src_backup", recursive=True)
# Returns (True, "Directory copied: src -> src_backup")
```

#### `mv(source: str, dest: str) -> tuple[bool, str]`
Move or rename a file/directory.
```python
success, msg = vfs.mv("old.txt", "new.txt")
# Returns (True, "Moved: old.txt -> new.txt")
```

#### `rm(name: str, recursive: bool = False) -> tuple[bool, str]`
Delete a file or directory.
```python
success, msg = vfs.rm("file.txt")
# Returns (True, "File removed: file.txt")

success, msg = vfs.rm("directory", recursive=True)
# Returns (True, "Directory removed: directory")
```

---

### `FileManager` (src/filesystem.py)

High-level wrapper around VirtualFileSystem that provides exception-based error handling.

**Attributes**:
- `vfs` (VirtualFileSystem): Underlying virtual filesystem

**Key Methods**:

All methods follow Unix conventions and raise standard exceptions:
- `FileNotFoundError`: When file/directory doesn't exist
- `FileExistsError`: When file/directory already exists
- `IsADirectoryError`: When operation fails because target is directory
- `NotADirectoryError`: When cd target is not a directory

#### `pwd() -> str`
```python
fm = FileManager()
cwd = fm.pwd()  # Returns "/" or "/path/to/dir"
```

#### `cd(path: str) -> str`
```python
try:
    fm.cd("projects")
    print(f"Now in {fm.pwd()}")
except FileNotFoundError as e:
    print(f"Directory not found: {e}")
```

#### `ls() -> list[tuple[str, str]]`
```python
items = fm.ls()
for name, type_ in items:
    if type_ == "dir":
        print(f"[DIR]  {name}")
    else:
        print(f"       {name}")
```

#### `mkdir(name: str) -> str`
```python
try:
    msg = fm.mkdir("newdir")
    print(msg)
except FileExistsError as e:
    print(f"Directory exists: {e}")
```

#### `touch(filename: str) -> str`
#### `cat(filename: str) -> str`
#### `echo(content: str, filename: str = None) -> str`
#### `cp(source: str, dest: str, recursive: bool = False) -> str`
#### `mv(source: str, dest: str) -> str`
#### `rm(name: str, recursive: bool = False) -> str`

All follow similar patterns to the examples above.

---

### `CommandParser` (src/parser.py)

Parses user input into command and arguments.

**Attributes**:
- None (stateless parser)

**Key Methods**:

#### `parse(command_line: str) -> ParsedCommand | None`
Parse a command line into components.
```python
parser = CommandParser()
result = parser.parse("mkdir projects")
if result:
    print(f"Command: {result.name}")
    print(f"Arguments: {result.arguments}")
    # Output:
    # Command: mkdir
    # Arguments: ['projects']
```

**Supported Features**:
- Quoted strings: `echo "hello world"` → arguments: ["hello world"]
- Multiple arguments: `cp -r src dest` → arguments: ["-r", "src", "dest"]
- Redirect operators: `echo test > file.txt` → arguments: ["test", ">", "file.txt"]
- Comment characters and empty input return `None`

---

### `CommandDispatcher` (src/commands.py)

Routes commands to their handler functions.

**Attributes**:
- `_commands` (dict): Internal command registry

**Key Methods**:

#### `register(name: str, function: Callable, aliases: list[str] = None)`
Register a command handler.
```python
dispatcher = CommandDispatcher()

def handle_hello(arguments: list[str]) -> None:
    print("Hello!")

dispatcher.register("hello", handle_hello, aliases=["hi", "hey"])
```

#### `execute(name: str, arguments: list[str]) -> bool`
Execute a registered command.
```python
executed = dispatcher.execute("hello", [])
# Returns True if command exists and was executed
# Returns False if command not found
```

#### `get_commands() -> list[str]`
Get sorted list of all registered command names (including aliases).
```python
commands = dispatcher.get_commands()
# Returns ["cat", "cd", "config", "cp", "echo", ...]
```

---

### `CommandHistory` (src/history.py)

Tracks command execution history.

**Attributes**:
- `entries` (list[HistoryEntry]): Command history
- `max_size` (int): Maximum history size (default 1000)

**Key Methods**:

#### `add(command: str, success: bool = True) -> None`
Add a command to history.
```python
history = CommandHistory()
history.add("pwd", success=True)
history.add("cd nonexistent", success=False)
```

#### `get_all() -> list[HistoryEntry]`
Get all history entries.
```python
entries = history.get_all()
for entry in entries:
    print(entry)  # Prints formatted entry with timestamp
```

#### `get_recent(count: int = 10) -> list[HistoryEntry]`
Get the most recent N entries.
```python
recent = history.get_recent(5)  # Last 5 commands
```

#### `search(pattern: str) -> list[HistoryEntry]`
Search history for pattern (case-insensitive).
```python
mkdir_commands = history.search("mkdir")
```

#### `clear() -> None`
Clear all history.
```python
history.clear()
```

#### `size() -> int`
Get current history size.
```python
num_commands = history.size()
```

---

### `Config` (src/config.py)

Manages shell configuration.

**Attributes**:
- `config` (dict): Configuration dictionary
- `config_file` (str): Path to config.json
- `DEFAULT_CONFIG` (dict): Default settings

**Key Methods**:

#### `get(key: str, default = None) -> Any`
Get a configuration value.
```python
config = Config()
theme = config.get("theme")  # "default"
unknown = config.get("unknown", "fallback")  # "fallback"
```

#### `set(key: str, value: Any) -> None`
Set a configuration value and save.
```python
config.set("theme", "dark")
```

#### `get_all() -> dict`
Get all configuration values.
```python
all_settings = config.get_all()
```

#### `reset_to_defaults() -> None`
Reset all settings to defaults.
```python
config.reset_to_defaults()
```

#### `load() -> None`
Load configuration from file.
```python
config.load()
```

#### `save() -> None`
Save configuration to file.
```python
config.save()
```

---

### `Logger` (src/logger.py)

Activity logging system.

**Attributes**:
- `log_file` (str): Path to log file
- `enabled` (bool): Logging enabled/disabled

**Key Methods**:

#### `info(message: str) -> None`
Log an info message.
```python
logger = Logger()
logger.info("Application started")
```

#### `command(cmd: str, success: bool = True) -> None`
Log a command execution.
```python
logger.command("mkdir projects", success=True)
logger.command("invalid", success=False)
```

#### `error(message: str) -> None`
Log an error.
```python
logger.error("Invalid path provided")
```

#### `warning(message: str) -> None`
Log a warning.
```python
logger.warning("Low disk space")
```

#### `session_start() -> None` and `session_end() -> None`
Log session lifecycle.
```python
logger.session_start()
# ... commands ...
logger.session_end()
```

#### `enable()` and `disable() -> None`
Control logging.
```python
logger.disable()  # Logging paused
logger.enable()   # Logging resumed
```

---

## Data Classes

### `VirtualFile`
Represents a file in virtual filesystem.
```python
@dataclass
class VirtualFile:
    name: str
    content: str = ""
    created_at: datetime
    modified_at: datetime
```

### `VirtualDirectory`
Represents a directory in virtual filesystem.
```python
@dataclass
class VirtualDirectory:
    name: str
    parent: VirtualDirectory | None
    children: dict[str, VirtualDirectory | VirtualFile]
    created_at: datetime
```

### `ParsedCommand`
Result of parsing a command line.
```python
@dataclass
class ParsedCommand:
    name: str
    arguments: list[str]
```

### `HistoryEntry`
Represents a command in history.
```python
@dataclass
class HistoryEntry:
    command: str
    timestamp: datetime
    success: bool
```

---

## Utility Functions (src/utils.py)

### `format_size(size_bytes: int) -> str`
Convert bytes to human-readable format.
```python
format_size(1024)  # "1.0KB"
format_size(1048576)  # "1.0MB"
```

### `validate_filename(filename: str) -> tuple[bool, str | None]`
Validate a filename.
```python
is_valid, error = validate_filename("file.txt")
```

### `validate_path(path: str) -> tuple[bool, str | None]`
Validate a path.
```python
is_valid, error = validate_path("/projects/src")
```

### `normalize_path(path: str) -> str`
Convert path to use forward slashes.
```python
normalize_path("path\\to\\file")  # "path/to/file"
```

---

## Error Handling

Punas Power Shell uses standard Python exceptions:

### Common Exceptions
- `FileNotFoundError`: File or directory doesn't exist
- `FileExistsError`: File or directory already exists
- `IsADirectoryError`: Operation failed because target is directory
- `NotADirectoryError`: Operation failed because target is file
- `ValueError`: Invalid argument or parsing error

### Example
```python
try:
    fm.cd("projects")
    fm.mkdir("src")
except FileNotFoundError:
    print("Directory not found")
except FileExistsError:
    print("Directory already exists")
```

---

## Testing

### Running Tests
```bash
# Unit tests (37 tests)
python test_units.py

# Integration tests (37 tests)
python test_shell_integration.py

# Virtual filesystem tests
python test_virtual_fs.py
```

### Writing Tests
```python
import unittest
from src.virtual_fs import VirtualFileSystem

class TestVFS(unittest.TestCase):
    def setUp(self):
        self.vfs = VirtualFileSystem()
    
    def test_mkdir_creates_directory(self):
        success, msg = self.vfs.mkdir("test")
        self.assertTrue(success)
        items = self.vfs.ls()
        self.assertIn(("test", "dir"), items)
```

---

## Performance Considerations

- **Memory**: All files stored in memory (Python objects)
- **Scalability**: Suitable for educational use; not for large-scale data
- **Speed**: In-memory operations are very fast
- **No Persistence**: Filesystem cleared when shell exits

---

## Extension Guide

### Adding a New Command

1. Implement handler method in PunasShell:
```python
def _mycommand_command(self, arguments: list[str]) -> None:
    """Handle mycommand."""
    if len(arguments) != 1:
        print("mycommand: expected 1 argument")
        return
    
    try:
        # Implementation here
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
```

2. Register in `_register_commands()`:
```python
self.dispatcher.register(
    "mycommand",
    self._mycommand_command,
    aliases=["my", "cmd"]
)
```

3. Test it:
```python
# Manual testing
shell = PunasShell()
shell.process_input("mycommand arg1")

# Unit test
def test_mycommand(self):
    shell = PunasShell()
    shell.process_input("mycommand arg1")
    # Assert expected behavior
```

---

For detailed command examples, see README_COMMANDS.md.
For architecture overview, see DEVELOPER_GUIDE.md.
