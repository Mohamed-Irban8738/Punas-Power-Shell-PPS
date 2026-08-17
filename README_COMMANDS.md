# Punas Power Shell - Command Reference

Complete documentation for all Punas Power Shell commands.

## Navigation Commands

### `pwd` - Print Working Directory
Display the current working directory path.

**Usage**: `pwd`

**Output**: Full path starting from root `/`

**Examples**:
```
psh> pwd
/

psh> mkdir projects
psh> cd projects
psh\projects> pwd
/projects

psh\projects> mkdir code
psh\projects> cd code
psh\projects\code> pwd
/projects/code
```

---

### `ls` - List Directory Contents
List all files and directories in the current directory.

**Usage**: `ls`

**Output Format**:
- Directories shown as `[DIR] dirname` (sorted alphabetically)
- Files shown as `       filename` (sorted alphabetically)
- Summary shows total file count

**Features**:
- Directories always listed first, then files
- Both sorted alphabetically within their type
- Shows friendly directory marker `[DIR]`

**Examples**:
```
psh> ls
[DIR]  projects
[DIR]  downloads
       README.md
       config.txt

Total files: 2

psh> cd projects
psh\projects> touch script.py
psh\projects> touch data.txt
psh\projects> mkdir src
psh\projects> ls
[DIR]  src
       data.txt
       script.py

Total files: 2
```

---

### `cd` - Change Directory
Change to a different directory.

**Usage**: `cd <path>`

**Path Types**:
- Absolute path: `/path/to/dir` (from root)
- Relative path: `dirname` (from current directory)
- Parent directory: `..` (go up one level)
- Current directory: `.` (stay in current directory)

**Error Cases**:
- Directory doesn't exist: `cd: no such file or directory`
- Path is a file: `cd: no such file or directory`

**Examples**:
```
psh> pwd
/

psh> mkdir -p projects/python/src
psh> cd projects
psh\projects> pwd
/projects

psh\projects> cd python
psh\projects\python> pwd
/projects/python

psh\projects\python> cd src
psh\projects\python\src> pwd
/projects/python/src

psh\projects\python\src> cd ..
psh\projects\python> pwd
/projects/python

psh\projects\python> cd /
psh> pwd
/

psh> cd projects/python/src
psh\projects\python\src> pwd
/projects/python/src
```

---

## File Operation Commands

### `touch` - Create Empty File
Create a new empty file or update its modification timestamp.

**Usage**: `touch <filename>`

**Behavior**:
- Creates an empty file with given name
- If file exists, updates its timestamp
- Fails if path is a directory

**Error Cases**:
- Empty filename: `touch: filename cannot be empty`
- Target is a directory: `touch: 'dirname' is a directory`

**Examples**:
```
psh> touch file.txt
File created: file.txt

psh> ls
       file.txt

psh> touch file.txt
File timestamp updated: file.txt

psh> mkdir dir
psh> touch dir
touch: 'dir' is a directory
```

---

### `mkdir` - Create Directory
Create a new directory in the current location.

**Usage**: `mkdir <dirname>`

**Behavior**:
- Creates empty directory with given name
- Fails if directory already exists
- Name cannot be empty

**Error Cases**:
- Directory exists: `mkdir: cannot create directory 'name': already exists`
- Empty name: `mkdir: name cannot be empty`

**Examples**:
```
psh> mkdir projects
Directory created: projects

psh> ls
[DIR]  projects

psh> mkdir projects
mkdir: cannot create directory 'projects': already exists

psh> cd projects
psh\projects> mkdir src
psh\projects> mkdir tests
psh\projects> ls
[DIR]  src
[DIR]  tests
```

---

### `cat` - Display File Contents
Show the contents of a file.

**Usage**: `cat <filename>`

**Behavior**:
- Displays entire file content
- Works with text files
- Fails if file doesn't exist or is directory

**Error Cases**:
- File not found: `cat: 'name': no such file or directory`
- Target is directory: `cat: 'name': is a directory`

**Examples**:
```
psh> echo Hello World > greeting.txt
Written to greeting.txt

psh> cat greeting.txt
Hello World

psh> echo Line 1 > data.txt
psh> cat data.txt
Line 1
```

---

### `echo` - Print Text or Write to File
Print text to console or write content to a file.

**Usage**: `echo <text> [> filename]`

**Without Redirection**:
- Prints text to console
- Multiple arguments joined with spaces

**With Redirection** (`>`):
- Writes text to file
- Creates file if it doesn't exist
- Overwrites file if it exists
- Shows confirmation message

**Error Cases**:
- No file after `>`: `echo: syntax error - no file after >`
- Target is directory: `echo: 'name': is a directory`

**Examples**:
```
psh> echo Hello
Hello

psh> echo This is a test
This is a test

psh> echo Hello World > greeting.txt
Written to greeting.txt

psh> cat greeting.txt
Hello World

psh> echo Updated content > greeting.txt
Written to greeting.txt

psh> cat greeting.txt
Updated content

psh> mkdir dir
psh> echo test > dir
echo: 'dir': is a directory
```

---

### `cp` - Copy Files or Directories
Copy a file or directory to a new location.

**Usage**: `cp [-r] <source> <destination>`

**Without `-r` Flag** (Files only):
- Copies single file to destination
- Fails if source is directory

**With `-r` Flag** (Recursive):
- Copies files
- Copies directories and all contents recursively
- Required when source is a directory

**Error Cases**:
- Source doesn't exist: `cp: 'source': no such file or directory`
- Source is directory without `-r`: `cp: 'source' is a directory (use -r)`
- Destination exists: `cp: 'dest' already exists`

**Examples**:
```
psh> touch file.txt
File created: file.txt

psh> echo Original > file.txt
Written to file.txt

psh> cp file.txt backup.txt
Copied: file.txt -> backup.txt

psh> cat backup.txt
Original

psh> mkdir src
psh> touch src/code.py
psh> cp -r src src_backup
Copied: src -> src_backup

psh> ls
[DIR]  src
[DIR]  src_backup
       file.txt
       backup.txt
```

---

### `mv` - Move or Rename Files
Move or rename a file or directory.

**Usage**: `mv <source> <destination>`

**Behavior**:
- Moves source to destination path
- Can be used to rename
- Works with files and directories

**Error Cases**:
- Source doesn't exist: `mv: cannot stat 'source': no such file or directory`
- Destination exists: `mv: 'dest' already exists`

**Examples**:
```
psh> touch old_name.txt
File created: old_name.txt

psh> mv old_name.txt new_name.txt
Moved: old_name.txt -> new_name.txt

psh> ls
       new_name.txt

psh> mkdir old_folder
psh> mv old_folder new_folder
Moved: old_folder -> new_folder

psh> ls
[DIR]  new_folder
```

---

### `rm` - Delete Files or Directories
Remove (delete) files or directories.

**Usage**: `rm [-r] <name>`

**Without `-r` Flag** (Files only):
- Deletes single file
- Fails if target is directory

**With `-r` Flag** (Recursive):
- Deletes files
- Deletes directories and all contents
- Required when target is a directory

**Error Cases**:
- Target doesn't exist: `rm: cannot remove 'name': no such file or directory`
- Target is directory without `-r`: `rm: cannot remove 'name': is a directory (use -r)`

**Examples**:
```
psh> touch temp.txt
File created: temp.txt

psh> rm temp.txt
Removed: temp.txt

psh> ls
(empty)

psh> mkdir temp_dir
psh> touch temp_dir/file.txt
psh> rm temp_dir
rm: cannot remove 'temp_dir': is a directory (use -r)

psh> rm -r temp_dir
Directory removed: temp_dir

psh> ls
(empty)
```

---

## Shell Management Commands

### `help` - Display Available Commands
Show a list of all available commands.

**Usage**: `help`

**Output**: Alphabetically sorted list of command names

**Examples**:
```
psh> help

Available commands:

  cat
  cd
  config
  cp
  echo
  exit
  help
  history
  ls
  mkdir
  mv
  pwd
  rm
  touch
```

---

### `history` - View or Manage Command History
View, search, or clear command history.

**Usage**:
- `history`: Show all commands
- `history <n>`: Show last n commands
- `history -s <pattern>`: Search for commands containing pattern
- `history -c`: Clear all history

**Behavior**:
- Default shows recent commands with numbering
- Search is case-insensitive
- Shows up to 1000 commands (configurable)

**Examples**:
```
psh> pwd
/

psh> mkdir projects
Directory created: projects

psh> cd projects
psh\projects> touch file.txt
File created: file.txt

psh\projects> history
  1. pwd
  2. mkdir projects
  3. cd projects
  4. touch file.txt

psh\projects> history 2
  3. cd projects
  4. touch file.txt

psh\projects> history -s mkdir
History entries matching 'mkdir':
  1. mkdir projects

psh\projects> history -c
History cleared

psh\projects> history
No history
```

---

### `config` - Manage Shell Configuration
View, modify, or reset shell configuration.

**Usage**:
- `config`: Show all configuration
- `config get <key>`: Get specific setting
- `config set <key> <value>`: Change setting
- `config reset`: Reset to defaults

**Default Settings**:
- `theme`: "default" - Color theme
- `prompt_format`: "psh" - Prompt format
- `history_size`: 1000 - Maximum history entries
- `log_file`: "shell.log" - Log file location
- `enable_logging`: True - Enable activity logging
- `colors_enabled`: False - Enable colored output
- `auto_cd`: False - Auto change directory

**Examples**:
```
psh> config
Current Configuration:
  theme: default
  prompt_format: psh
  history_size: 1000
  log_file: shell.log
  enable_logging: True
  colors_enabled: False
  auto_cd: False

psh> config get theme
theme: default

psh> config set theme dark
Configuration updated: theme = dark

psh> config get theme
theme: dark

psh> config set history_size 500
Configuration updated: history_size = 500

psh> config reset
Configuration reset to defaults
```

---

### `exit` (alias: `quit`)
Terminate the Punas Power Shell session.

**Usage**: `exit` or `quit`

**Behavior**:
- Closes the shell
- Logs session end
- Displays goodbye message
- Saves any pending state

**Examples**:
```
psh> exit
Shutting down Punas Shell...
Goodbye!

(Shell closes)
```

---

## Common Use Cases

### Creating a Project Structure
```
psh> mkdir -p projects/myapp/src
psh> mkdir -p projects/myapp/tests
psh> cd projects/myapp
psh\projects\myapp> touch src/main.py
psh\projects\myapp> touch tests/test_main.py
```

### Working with Files
```
psh> echo "#!/usr/bin/env python" > script.py
psh> echo print('Hello') >> script.py
psh> cat script.py
psh> cp script.py script_backup.py
```

### Cleanup
```
psh> rm temporary_file.txt
psh> rm -r temporary_directory
```

### Viewing History and Config
```
psh> history -s echo
psh> config get log_file
psh> config set prompt_format verbose
```

---

## Tips and Tricks

1. **Use `.` and `..` for navigation**
   ```
   cd ..      # Go to parent
   cd .       # Stay in current (rarely useful)
   ```

2. **Chain commands with cd and ls**
   ```
   cd directory
   ls         # See what's there
   cd ..      # Go back
   ```

3. **Use history to see what you did**
   ```
   history -s mkdir    # Find all mkdir commands
   ```

4. **Backup important files**
   ```
   cp important.txt important_backup.txt
   ```

5. **Use echo for quick file creation**
   ```
   echo "content" > newfile.txt
   ```

---

For more information, run `help` or check the main README.md file.
