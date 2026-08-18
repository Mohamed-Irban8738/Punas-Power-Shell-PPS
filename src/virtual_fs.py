"""
Virtual filesystem implementation for Punas Power Shell.
Provides an in-memory filesystem isolated from the real system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class VirtualFile:
    """Represents a file in the virtual filesystem."""
    
    name: str
    content: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    
    def update_content(self, new_content: str) -> None:
        """Update file content and timestamp."""
        self.content = new_content
        self.modified_at = datetime.now()
    
    def __repr__(self) -> str:
        return f"VirtualFile({self.name})"


@dataclass
class VirtualDirectory:
    """Represents a directory in the virtual filesystem."""
    
    name: str
    parent: Optional["VirtualDirectory"] = None
    children: dict[str, "VirtualDirectory | VirtualFile"] = field(
        default_factory=dict
    )
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_child(
        self, 
        child: "VirtualDirectory | VirtualFile"
    ) -> None:
        """Add a child file or directory."""
        self.children[child.name] = child
    
    def remove_child(self, name: str) -> None:
        """Remove a child file or directory."""
        if name in self.children:
            del self.children[name]
    
    def get_child(self, name: str) -> Optional["VirtualDirectory | VirtualFile"]:
        """Get a child by name."""
        return self.children.get(name)
    
    def is_empty(self) -> bool:
        """Check if directory is empty."""
        return len(self.children) == 0
    
    def __repr__(self) -> str:
        return f"VirtualDirectory({self.name})"


class VirtualFileSystem:
    """In-memory virtual filesystem for safe command execution."""
    
    def __init__(self) -> None:
        """Initialize the virtual filesystem and populate default structure."""
        self.root = VirtualDirectory(name="")
        self.current_directory = self.root

        # Helper to create nested directories (creates parents as needed)
        def _mkpath(parts: list[str]) -> VirtualDirectory:
            cur = self.root
            for part in parts:
                child = cur.get_child(part)
                if child is None:
                    new_dir = VirtualDirectory(name=part, parent=cur)
                    cur.add_child(new_dir)
                    cur = new_dir
                else:
                    if isinstance(child, VirtualDirectory):
                        cur = child
                    else:
                        # If a file exists where a dir is expected, stop and return current
                        return cur
            return cur

        # Build the directory tree as specified
        _mkpath(["bin"])
        _mkpath(["etc"])
        _mkpath(["home", "student", "Desktop"])
        _mkpath(["home", "student", "Documents"])
        _mkpath(["home", "student", "Downloads"])
        _mkpath(["home", "student", "Projects", "Python"])
        _mkpath(["home", "student", "Projects", "Linux"])
        _mkpath(["home", "student"])
        _mkpath(["tmp"])
        _mkpath(["usr", "bin"])
        _mkpath(["usr", "lib"])
        _mkpath(["var", "log"])

        # Shortcuts to directories
        bin_dir = self.root.get_child("bin")
        etc_dir = self.root.get_child("etc")
        home_student = self.root.get_child("home").get_child("student")
        tmp_dir = self.root.get_child("tmp")
        usr_bin = self.root.get_child("usr").get_child("bin")
        var_log = self.root.get_child("var").get_child("log")

        # Add mock executables in /bin
        if isinstance(bin_dir, VirtualDirectory):
            bin_dir.add_child(VirtualFile(name="bash", content="#!/bin/sh\necho \"bash (mock)\"\n"))
            bin_dir.add_child(VirtualFile(name="cat", content="#!/bin/sh\n# mock cat\n"))
            bin_dir.add_child(VirtualFile(name="cp", content="#!/bin/sh\n# mock cp\n"))
            bin_dir.add_child(VirtualFile(name="ls", content="#!/bin/sh\n# mock ls\n"))
            bin_dir.add_child(VirtualFile(name="pwd", content="#!/bin/sh\n# mock pwd\n"))

        # Add /etc files
        if isinstance(etc_dir, VirtualDirectory):
            etc_dir.add_child(VirtualFile(name="hostname", content="punas-vm\n"))
            etc_dir.add_child(VirtualFile(name="os-release", content="NAME=\"Punas Linux\"\nVERSION=\"0.1-mock\"\n"))

        # Add home/student files
        if isinstance(home_student, VirtualDirectory):
            desktop = home_student.get_child("Desktop")
            if isinstance(desktop, VirtualDirectory):
                desktop.add_child(VirtualFile(name="welcome.txt", content="Welcome to Punas Power Shell!\n"))

            docs = home_student.get_child("Documents")
            if isinstance(docs, VirtualDirectory):
                docs.add_child(VirtualFile(name="notes.txt", content="These are some sample notes.\n"))
                docs.add_child(VirtualFile(name="report.txt", content="This is a mock report.\n"))

            downloads = home_student.get_child("Downloads")
            if isinstance(downloads, VirtualDirectory):
                downloads.add_child(VirtualFile(name="sample.pdf", content="%PDF-1.4 (mock PDF content)\n"))

            projects = home_student.get_child("Projects")
            if isinstance(projects, VirtualDirectory):
                python_proj = projects.get_child("Python")
                if isinstance(python_proj, VirtualDirectory):
                    python_proj.add_child(VirtualFile(name="hello.py", content="print('Hello from mock Python project')\n"))

                linux_proj = projects.get_child("Linux")
                if isinstance(linux_proj, VirtualDirectory):
                    linux_proj.add_child(VirtualFile(name="commands.txt", content="ls\npc\ncat\n"))

            home_student.add_child(VirtualFile(name="README.txt", content="Student home directory (mock).\n"))

        # Add /tmp content
        if isinstance(tmp_dir, VirtualDirectory):
            tmp_dir.add_child(VirtualFile(name="temp.txt", content="temporary file\n"))

        # Add /var/log/system.log
        if isinstance(var_log, VirtualDirectory):
            var_log.add_child(VirtualFile(name="system.log", content="[INFO] Mock system log initialized\n"))

        # Ensure /usr/bin exists (empty) and /usr/lib exists
        if isinstance(usr_bin, VirtualDirectory):
            usr_bin.add_child(VirtualFile(name="mockutil", content="# mock util\n"))
    
    def get_path_parts(self, path: str) -> list[str]:
        """Split a path into components."""
        # Normalize path separators to forward slashes
        path = path.replace("\\", "/")
        path = path.strip("/")
        
        if not path:
            return []
        
        return path.split("/")
    
    def resolve_path(
        self, 
        path: str
    ) -> tuple[VirtualDirectory, list[str]]:
        """
        Resolve a path starting from current or root directory.
        Returns (starting_directory, remaining_parts).
        """
        parts = self.get_path_parts(path)
        
        # Absolute path starts from root
        if path.startswith("/"):
            return (self.root, parts)
        
        # Relative path starts from current directory
        return (self.current_directory, parts)
    
    def navigate_to(
        self, 
        start_dir: VirtualDirectory,
        parts: list[str]
    ) -> tuple[VirtualDirectory, Optional[str]]:
        """
        Navigate through directory parts.
        Returns (final_directory, error_message).
        error_message is None if successful.
        """
        current = start_dir
        
        for i, part in enumerate(parts):
            if part == ".":
                continue
            
            if part == "..":
                if current.parent:
                    current = current.parent
                continue
            
            child = current.get_child(part)
            
            if child is None:
                # Return what we navigated to and what we couldn't find
                remaining = "/".join(parts[i:])
                return (current, remaining)
            
            if not isinstance(child, VirtualDirectory):
                # Hit a file, can't navigate further
                remaining = "/".join(parts[i:])
                return (current, remaining)
            
            current = child
        
        return (current, None)
    
    def pwd(self) -> str:
        """Get current working directory path."""
        parts = []
        current = self.current_directory
        
        while current.parent is not None:
            parts.append(current.name)
            current = current.parent
        
        if not parts:
            return "/"
        
        return "/" + "/".join(reversed(parts))
    
    def ls(self) -> list[tuple[str, str]]:
        """
        List contents of current directory.
        Returns list of (name, type) tuples where type is 'dir' or 'file'.
        Directories come first, then files, both sorted alphabetically.
        """
        dirs = sorted(
            [(name, "dir") for name, child in self.current_directory.children.items()
             if isinstance(child, VirtualDirectory)],
            key=lambda x: x[0].lower()
        )
        
        files = sorted(
            [(name, "file") for name, child in self.current_directory.children.items()
             if isinstance(child, VirtualFile)],
            key=lambda x: x[0].lower()
        )
        
        return dirs + files
    
    def cd(self, path: str) -> tuple[bool, str]:
        """
        Change current directory.
        Returns (success, message).
        """
        if not path:
            return (False, "cd: path cannot be empty")
        
        start_dir, parts = self.resolve_path(path)
        target_dir, error = self.navigate_to(start_dir, parts)
        
        if error:
            return (False, f"cd: no such file or directory: {path}")
        
        self.current_directory = target_dir
        return (True, "")
    
    def mkdir(self, name: str) -> tuple[bool, str]:
        """
        Create a directory in current directory.
        Returns (success, message).
        """
        if not name:
            return (False, "mkdir: name cannot be empty")
        
        if name in self.current_directory.children:
            return (False, f"mkdir: cannot create directory '{name}': already exists")
        
        new_dir = VirtualDirectory(name=name, parent=self.current_directory)
        self.current_directory.add_child(new_dir)
        return (True, f"Directory created: {name}")
    def rmdir(self, name: str) -> tuple[bool, str]:
        """
        Remove an empty directory.

        Returns:
            Tuple containing success status and message.
        """
        if not name:
            return (False, "rmdir: name cannot be empty")

        child = self.current_directory.get_child(name)

        if child is None:
            return (
                False,
                f"rmdir: failed to remove '{name}': "
                "No such file or directory",
            )

        if isinstance(child, VirtualFile):
            return (
                False,
                f"rmdir: failed to remove '{name}': "
                "Not a directory",
            )

        if not child.is_empty():
            return (
                False,
                f"rmdir: failed to remove '{name}': "
                "Directory not empty",
            )

        self.current_directory.remove_child(name)

        return (True, f"Directory removed: {name}")
    def touch(self, filename: str) -> tuple[bool, str]:
        """
        Create an empty file or update its timestamp.
        Returns (success, message).
        """
        if not filename:
            return (False, "touch: filename cannot be empty")
        
        existing = self.current_directory.get_child(filename)
        
        if existing:
            if isinstance(existing, VirtualFile):
                existing.modified_at = datetime.now()
                return (True, f"File timestamp updated: {filename}")
            else:
                return (False, f"touch: '{filename}' is a directory")
        
        new_file = VirtualFile(name=filename)
        self.current_directory.add_child(new_file)
        return (True, f"File created: {filename}")
    
    def cat(self, filename: str) -> tuple[bool, str]:
        """
        Display file contents.
        Returns (success, content_or_error_message).
        """
        if not filename:
            return (False, "cat: filename cannot be empty")
        
        child = self.current_directory.get_child(filename)
        
        if child is None:
            return (False, f"cat: '{filename}': no such file or directory")
        
        if not isinstance(child, VirtualFile):
            return (False, f"cat: '{filename}': is a directory")
        
        return (True, child.content)
    
    def echo(self, content: str, filename: Optional[str] = None) -> tuple[bool, str]:
        """
        Print content or write to file.
        If filename is None, return content to print.
        If filename is provided, write content to file.
        Returns (success, output).
        """
        if filename:
            # Write to file
            existing = self.current_directory.get_child(filename)
            
            if existing and not isinstance(existing, VirtualFile):
                return (False, f"echo: '{filename}': is a directory")
            
            if existing:
                existing.update_content(content)
            else:
                new_file = VirtualFile(name=filename, content=content)
                self.current_directory.add_child(new_file)
            
            return (True, f"Written to {filename}")
        else:
            # Print to output
            return (True, content)
    def write(self, filename: str, content: str) -> str:
        """
        Write content to a file.

        Creates the file if it does not exist.
        Replaces existing file content if it exists.
        Raises FileNotFoundError or IsADirectoryError when appropriate.
        """
        if not filename:
            raise ValueError("write: filename cannot be empty")

        success, message = self.vfs.echo(content, filename)

        if not success:
            if "is a directory" in message:
                raise IsADirectoryError(message)
            raise FileNotFoundError(message)

        return message
    def rm(self, name: str, recursive: bool = False) -> tuple[bool, str]:
        """
        Delete a file or directory.
        Returns (success, message).
        """
        if not name:
            return (False, "rm: name cannot be empty")
        
        child = self.current_directory.get_child(name)
        
        if child is None:
            return (False, f"rm: cannot remove '{name}': no such file or directory")
        
        if isinstance(child, VirtualDirectory):
            if not recursive:
                return (False, f"rm: cannot remove '{name}': is a directory (use -r)")
            
            self.current_directory.remove_child(name)
            return (True, f"Directory removed: {name}")
        else:
            self.current_directory.remove_child(name)
            return (True, f"File removed: {name}")
    
    def cp(self, source: str, dest: str, recursive: bool = False) -> tuple[bool, str]:
        """
        Copy a file or directory.
        Returns (success, message).
        """
        if not source or not dest:
            return (False, "cp: both source and destination required")
        
        source_child = self.current_directory.get_child(source)
        
        if source_child is None:
            return (False, f"cp: '{source}': no such file or directory")
        
        if isinstance(source_child, VirtualDirectory):
            if not recursive:
                return (False, f"cp: '{source}' is a directory (use -r)")
            
            # Recursive copy of directory
            new_dir = VirtualDirectory(name=dest, parent=self.current_directory)
            self._copy_directory_contents(source_child, new_dir)
            self.current_directory.add_child(new_dir)
            return (True, f"Directory copied: {source} -> {dest}")
        else:
            # Copy file
            new_file = VirtualFile(
                name=dest,
                content=source_child.content
            )
            self.current_directory.add_child(new_file)
            return (True, f"File copied: {source} -> {dest}")
    
    def _copy_directory_contents(
        self,
        source_dir: VirtualDirectory,
        dest_dir: VirtualDirectory
    ) -> None:
        """Recursively copy directory contents."""
        for name, child in source_dir.children.items():
            if isinstance(child, VirtualDirectory):
                new_dir = VirtualDirectory(name=name, parent=dest_dir)
                self._copy_directory_contents(child, new_dir)
                dest_dir.add_child(new_dir)
            else:
                new_file = VirtualFile(
                    name=name,
                    content=child.content
                )
                dest_dir.add_child(new_file)
    
    def mv(self, source: str, dest: str) -> tuple[bool, str]:
        """
        Move or rename a file or directory.
        Returns (success, message).
        """
        if not source or not dest:
            return (False, "mv: both source and destination required")
        
        child = self.current_directory.get_child(source)
        
        if child is None:
            return (False, f"mv: cannot stat '{source}': no such file or directory")
        
        if dest in self.current_directory.children:
            return (False, f"mv: '{dest}' already exists")
        
        # Rename by updating the name and removing/readding
        self.current_directory.remove_child(source)
        child.name = dest
        self.current_directory.add_child(child)
        
        return (True, f"Moved: {source} -> {dest}")
