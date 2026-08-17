# Punas Power Shell (PPS)

A **safe, educational, in-memory shell implementation** built with Python that operates on a virtual filesystem. Punas Power Shell provides a Linux-like command-line experience without touching your real file system, making it perfect for learning and teaching shell commands.

## Features

### 🔐 **Safe Execution**
- **Isolated Virtual Filesystem**: All operations run on an in-memory filesystem, completely isolated from your real system
- **No File System Access**: Users can safely explore shell commands without risk of accidentally modifying real files
- **Perfect for Education**: Students can learn and practice shell commands in a sandboxed environment

### 📚 **Rich Command Set**
- **File Navigation**: pwd, ls, cd
- **File Operations**: touch, cat, echo, cp, rm, mv, mkdir
- **Shell Features**: help, exit, history, config

### 🎯 **Developer-Friendly**
- **Modular Architecture**: Clean separation of concerns
- **Comprehensive Tests**: 37 unit tests + 37 integration tests (all passing)
- **Extensible Design**: Easy to add new commands and features

## Quick Start

```bash
# Run the shell
python main.py
```

### Basic Commands

```
psh> pwd
/

psh> mkdir projects
Directory created: projects

psh> cd projects
psh\projects> touch hello.py

psh> exit
Goodbye!
```

## Command Reference

**Navigation**: pwd, cd, ls
**File Operations**: touch, mkdir, cat, echo, cp, mv, rm
**Shell Features**: help, exit, history, config

See README_COMMANDS.md for detailed command documentation.

## Testing

```bash
python test_units.py              # 37 unit tests
python test_shell_integration.py  # 37 integration tests  
python test_virtual_fs.py         # Virtual filesystem tests
```

**Result**: All 74+ tests passing (100% pass rate)

## Architecture

**Core Components**:
- PunasShell: Main shell engine
- CommandParser: Parse user commands
- VirtualFileSystem: In-memory filesystem (no real file access)
- FileManager: High-level filesystem API
- CommandHistory: Track command history
- Config: Configuration management
- Logger: Activity logging

**Safety**: All file operations happen in virtual filesystem only.

## Status

✅ Completed (13/22 tasks):
- Virtual filesystem implementation
- All 8 file manipulation commands  
- Shell engine with parsing and dispatch
- History tracking and logging
- Configuration management
- 74+ comprehensive tests
- Complete documentation

## Learn More

- **README_COMMANDS.md**: Detailed command reference
- **API_DOCUMENTATION.md**: Class and method documentation
- **DEVELOPER_GUIDE.md**: Architecture and how to extend

## License

Educational project for learning and teaching.

---

**Start learning shell commands safely with Punas Power Shell!**
