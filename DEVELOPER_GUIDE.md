# Punas Power Shell - Developer Guide

Architecture overview and guide for developers working on PPS.

## Project Overview

Punas Power Shell (PPS) is an educational shell implementation that provides a **safe, in-memory filesystem** where users can practice shell commands without accessing the real filesystem.

### Key Design Principles

1. **Safety First**: All operations on virtual filesystem only
2. **Educational**: Clear, understandable code suitable for learning
3. **Modularity**: Separated concerns with independent components
4. **Extensibility**: Easy to add new commands and features
5. **Testability**: Comprehensive test coverage (74+ tests)

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      PunasShell                            │
│  (Main shell engine, command registration, main loop)      │
└───────────────┬─────────────────────────────────────────────┘
                │
    ┌───────────┼───────────┬───────────┬──────────┐
    │           │           │           │          │
    ▼           ▼           ▼           ▼          ▼
CommandParser  Command    FileManager History   Config
(Parse input) Dispatcher  (File ops)  (Track)   (Settings)
              (Route cmds)   │
                             ▼
                      VirtualFileSystem
                   (In-memory filesystem)
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
    VirtualFile   VirtualDirectory    Tree Structure
   (File object)  (Directory object)   (Navigation)
```

### Data Flow

```
User Input
    │
    ▼
CommandParser.parse() ──► ParsedCommand(name, arguments)
    │
    ▼
CommandDispatcher.execute() ──► Handler function
    │
    ▼
FileManager methods ──► (Exception-based errors)
    │
    ▼
VirtualFileSystem methods ──► (Tuple[bool, str] results)
    │
    ▼
Output to Console / File Operations
```

---

## Module Reference

### `shell.py` - Core Shell Engine

**Responsibilities**:
- Main interactive loop
- Command registration and dispatch
- Prompt generation based on current directory
- User input processing
- Command history and logging integration

**Key Components**:
- `PunasShell` class: Main shell controller
- `_register_commands()`: Register all available commands
- Command handler methods: `_pwd_command()`, `_ls_command()`, etc.

**Example Handler Pattern**:
```python
def _mycommand_command(self, arguments: list[str]) -> None:
    """Handle mycommand command."""
    # Validate arguments
    if len(arguments) != expected_count:
        print(f"mycommand: expected {expected_count} arguments")
        return
    
    # Process
    try:
        # Call FileManager methods
        result = self.file_manager.some_operation(arguments[0])
        print(f"Success: {result}")
        
        # Log if needed
        self.logger.info(f"Operation completed")
    
    except FileNotFoundError as e:
        print(e)
    except FileExistsError as e:
        print(e)
    except Exception as e:
        print(f"Error: {e}")
```

### `virtual_fs.py` - Virtual Filesystem

**Responsibilities**:
- In-memory file and directory storage
- Path resolution and navigation
- File operations (create, read, write, delete)
- Directory operations (create, list, remove)

**Data Structures**:
- `VirtualFile`: Dataclass with name, content, timestamps
- `VirtualDirectory`: Dataclass with name, parent, children dict
- Tree structure: Directories can contain files and directories

**Key Design Decisions**:
- Using dictionaries for O(1) lookup of children
- Storing parent reference for easy backtracking
- Path normalization to handle both `/` and `\`
- Return tuples `(success: bool, message: str)` for error handling

### `filesystem.py` - FileManager Wrapper

**Responsibilities**:
- High-level filesystem API
- Exception-based error handling
- Conversion from tuple results to standard Python exceptions

**Conversion Examples**:
```python
# VirtualFileSystem returns:
success, error = vfs.mkdir("name")
if not success:
    raise FileExistsError(error)

# Client code uses standard exceptions:
try:
    fm.mkdir("name")
except FileExistsError:
    handle_duplicate()
```

### `parser.py` - Command Parser

**Responsibilities**:
- Parse user input into command and arguments
- Handle quoted strings
- Preserve special characters and operators
- Return None for empty input

**Implementation Details**:
- Uses Python's `shlex.split()` for robust parsing
- Handles quotes, escape sequences
- Case-insensitive command names (converted to lowercase)
- Preserves argument order and special characters

**Usage**:
```python
parser = CommandParser()
result = parser.parse("echo 'hello world' > file.txt")
# result.name = "echo"
# result.arguments = ["hello world", ">", "file.txt"]
```

### `commands.py` - Command Dispatcher

**Responsibilities**:
- Register command handlers
- Route commands to appropriate handlers
- Support command aliases

**Registry Pattern**:
```python
dispatcher = CommandDispatcher()

# Register with optional aliases
dispatcher.register(
    "command_name",
    handler_function,
    aliases=["alias1", "alias2"]
)

# Execute
if dispatcher.execute("command_name", arguments):
    print("Command executed")
else:
    print("Unknown command")
```

### `history.py` - Command History

**Responsibilities**:
- Track executed commands with timestamps
- Provide search capability
- Enforce size limits
- Store success/failure status

**Features**:
- Circular buffer (oldest entries removed when full)
- Timestamped entries
- Case-insensitive search
- Size limit (default 1000)

### `config.py` - Configuration Management

**Responsibilities**:
- Store and load configuration from JSON
- Provide get/set interface
- Merge with defaults
- Save changes automatically

**Storage**:
- File: `config.json`
- Format: JSON
- Auto-creates if missing
- Auto-saves on `set()`

**Default Settings**:
```python
{
    "theme": "default",
    "prompt_format": "psh",
    "history_size": 1000,
    "log_file": "shell.log",
    "enable_logging": true,
    "colors_enabled": false,
    "auto_cd": false
}
```

### `logger.py` - Activity Logging

**Responsibilities**:
- Log commands and results
- Log filesystem operations
- Log errors and warnings
- Session lifecycle tracking

**Log Format**:
```
[2024-01-15 10:30:45] SESSION  | Shell session started
[2024-01-15 10:30:46] COMMAND  | [SUCCESS] mkdir projects
[2024-01-15 10:30:47] COMMAND  | [SUCCESS] cd projects
[2024-01-15 10:30:48] SESSION  | Shell session ended
```

### `utils.py` - Utility Functions

**Responsibilities**:
- File format utilities
- Validation functions
- String manipulation
- Path normalization

**Available Functions**:
- `format_size()`: Bytes to human-readable
- `validate_filename()`: Check valid filename
- `validate_path()`: Check valid path
- `normalize_path()`: Convert to forward slashes
- `truncate_string()`: Limit string length
- `pluralize()`: Grammar helpers

---

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone <repo>
cd Punas-Power-Shell

# Run the shell
python main.py

# Run tests
python test_units.py
python test_shell_integration.py
python test_virtual_fs.py
```

### Adding a New Command

#### Step 1: Implement the Handler
In `src/shell.py`, add a new method following the pattern:

```python
def _newcommand_command(self, arguments: list[str]) -> None:
    """Handle newcommand.
    
    Usage: newcommand <arg1> [<arg2>]
    """
    # Validate argument count
    if len(arguments) < 1:
        print("newcommand: requires at least 1 argument")
        return
    
    # Unpack arguments
    arg1 = arguments[0]
    arg2 = arguments[1] if len(arguments) > 1 else None
    
    # Call FileManager
    try:
        result = self.file_manager.some_operation(arg1, arg2)
        print(f"Success: {result}")
        self.logger.info(f"newcommand executed with {arg1}")
    
    except FileNotFoundError as error:
        print(f"Error: {error}")
        self.logger.error(str(error))
    except FileExistsError as error:
        print(f"Error: {error}")
    except Exception as error:
        print(f"Unexpected error: {error}")
        self.logger.error(f"newcommand failed: {error}")
```

#### Step 2: Register the Command
In `_register_commands()`:

```python
self.dispatcher.register(
    "newcommand",
    self._newcommand_command,
    aliases=["nc", "new"]  # Optional aliases
)
```

#### Step 3: Write Tests
In `test_units.py` and/or `test_shell_integration.py`:

```python
class TestNewCommand(unittest.TestCase):
    def setUp(self):
        self.shell = PunasShell()
    
    def test_newcommand_success(self):
        # Test normal operation
        self.shell.process_input("newcommand arg1")
        # Assert expected behavior
    
    def test_newcommand_error(self):
        # Test error handling
        self.shell.process_input("newcommand")  # Missing arg
        # Assert error message
```

#### Step 4: Add to Documentation
- Update README_COMMANDS.md with command reference
- Update API_DOCUMENTATION.md with handler documentation

#### Step 5: Test and Verify
```bash
# Run tests
python test_units.py
python test_shell_integration.py

# Manual testing
python main.py
psh> help  # Should show newcommand
psh> newcommand arg1
```

---

## Testing Strategy

### Test Organization

**test_units.py** - Component tests
- Each class tested independently
- 37 test cases covering:
  - CommandParser (7 tests)
  - VirtualFileSystem (19 tests)
  - FileManager (4 tests)
  - CommandHistory (5 tests)
  - Config (5 tests)

**test_shell_integration.py** - End-to-end tests
- Real workflows tested
- 37 test cases covering:
  - Parser integration (6 tests)
  - Filesystem operations (9 tests)
  - Complete shell workflows (22 tests)

**test_virtual_fs.py** - Virtual filesystem tests
- Original comprehensive tests
- All 14 tests passing

### Running Tests

```bash
# All unit tests
python test_units.py

# All integration tests
python test_shell_integration.py

# Specific test class
python -m unittest test_units.TestVirtualFileSystem

# Specific test
python -m unittest test_units.TestVirtualFileSystem.test_mkdir_creates_directory
```

### Test Coverage

```
Component               Tests   Status
────────────────────────────────────────
CommandParser            7      [PASS]
VirtualFileSystem       19      [PASS]
FileManager              4      [PASS]
CommandHistory           5      [PASS]
Config                   5      [PASS]
Shell Integration       37      [PASS]
────────────────────────────────────────
Total                   74      [PASS] ✓
```

### Writing New Tests

```python
import unittest
from src.shell import PunasShell
from src.filesystem import FileManager

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.shell = PunasShell()
        self.fm = FileManager()
    
    def test_feature_works(self):
        """Test that feature works correctly."""
        self.fm.mkdir("test")
        items = self.fm.ls()
        self.assertIn(("test", "dir"), items)
    
    def test_feature_error_handling(self):
        """Test error cases."""
        with self.assertRaises(FileExistsError):
            self.fm.mkdir("test")
            self.fm.mkdir("test")  # Duplicate

if __name__ == "__main__":
    unittest.main()
```

---

## Code Style Guidelines

### Python Style
- Follow PEP 8
- Use type hints for functions
- Document all classes and public methods
- Use descriptive variable names
- Keep functions focused and small

### Naming Conventions
- Classes: `PascalCase` (e.g., `VirtualFileSystem`)
- Functions/Methods: `snake_case` (e.g., `get_prompt`)
- Constants: `UPPER_CASE` (e.g., `DEFAULT_PROMPT`)
- Private methods: Prefix with `_` (e.g., `_register_commands`)

### Documentation
- Module docstring at top of file
- Class docstring explaining purpose
- Method docstring with parameters and return value
- Complex logic commented inline

```python
def complex_function(arg1: str, arg2: int) -> dict:
    """
    Brief description of what function does.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When arg2 is negative
    """
    # Implementation
    pass
```

---

## Debugging Tips

### Enable Logging
```python
# Check shell.log for detailed activity
tail -f shell.log

# Look for errors and commands
grep ERROR shell.log
grep COMMAND shell.log
```

### Print Debugging
```python
# Add temporary prints
vfs = VirtualFileSystem()
print(f"DEBUG: pwd = {vfs.pwd()}")
print(f"DEBUG: ls = {vfs.ls()}")
```

### Interactive Testing
```python
# Start Python REPL
python

# Import and test components
from src.virtual_fs import VirtualFileSystem
vfs = VirtualFileSystem()
vfs.mkdir("test")
print(vfs.ls())

# Test parser
from src.parser import CommandParser
parser = CommandParser()
result = parser.parse("echo hello")
print(result.name, result.arguments)
```

### Unit Test Debugging
```python
# Run with verbose output
python -m unittest test_units.TestVirtualFileSystem -v

# Run single test with print debugging
python -m unittest test_units.TestVirtualFileSystem.test_mkdir_creates_directory -v
```

---

## Performance Optimization

### Current Performance
- Command parsing: < 1ms
- File operations: < 1ms (in-memory)
- Directory listing: < 1ms
- History search: < 1ms

### Future Optimizations
- Cache directory listings
- Optimize path resolution for deep trees
- Lazy load configuration files

---

## Security Considerations

### Current Design
- ✅ All operations on virtual filesystem only
- ✅ No real filesystem access
- ✅ Input parsing with shlex (safe against injection)
- ✅ No shell metacharacter execution

### Potential Enhancements
- Add permission checking
- Implement file ownership
- Add audit logging
- Rate limiting for history

---

## Deployment

### Development
```bash
python main.py
```

### Testing
```bash
python test_units.py
python test_shell_integration.py
python test_virtual_fs.py
```

### Distribution
```bash
# Package for distribution
# (Future: add setup.py, requirements.txt, etc.)
```

---

## Troubleshooting

### Command not found
- Check `help` for registered commands
- Verify command registered in `_register_commands()`

### File not found errors
- Check path is correct (absolute vs relative)
- Use `ls` to verify directory contents
- Check `pwd` to see current directory

### Test failures
- Run tests individually to isolate issue
- Check test setup/teardown
- Review error message carefully
- Add print debugging to test

### Unicode/Encoding errors
- Python 3 required (Python 3.7+)
- Set UTF-8 encoding: `sys.stdout = io.TextIOWrapper(...)`
- Check log file encoding

---

## Future Work

### Planned Features
- Permission system (chmod, chown)
- Wildcards support (* and ?)
- Environment variables
- Pipes and redirects
- Script files (.psh)
- Session persistence

### Known Limitations
- No real filesystem access (by design)
- No system commands
- No network operations
- Limited to text files

---

## References

- **Python Docs**: https://docs.python.org/3/
- **PEP 8**: https://www.python.org/dev/peps/pep-0008/
- **Unix Shell**: https://pubs.opengroup.org/onlinepubs/9699919799/utilities/

---

For questions or contributions, refer to README.md and API_DOCUMENTATION.md.
