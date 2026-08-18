"""
Filesystem operations for Punas Power Shell.
Uses virtual filesystem for safe, isolated file operations.
"""

from src.virtual_fs import VirtualFileSystem


class FileManager:
    """Manage filesystem operations for the shell using virtual filesystem."""

    def __init__(self) -> None:
        """Initialize the file manager with virtual filesystem."""
        self.vfs = VirtualFileSystem()

    def pwd(self) -> str:
        """Return the current working directory."""
        return self.vfs.pwd()

    def ls(self) -> list[tuple[str, str]]:
        """
        Return the contents of the current directory.
        Returns list of (name, type) tuples.
        Directories are returned before files, both sorted alphabetically.
        """
        return self.vfs.ls()

    def cd(self, path: str) -> str:
        """
        Change the current working directory.
        Raises FileNotFoundError if path doesn't exist.
        Raises NotADirectoryError if path is not a directory.
        """
        success, error_msg = self.vfs.cd(path)
        
        if not success:
            if "no such file or directory" in error_msg:
                raise FileNotFoundError(error_msg)
            raise NotADirectoryError(error_msg)
        
        return self.vfs.pwd()

    def mkdir(self, name: str) -> str:
        """
        Create a new directory.
        Raises FileExistsError if directory already exists.
        """
        success, msg = self.vfs.mkdir(name)
        
        if not success:
            raise FileExistsError(msg)
        
        return msg
    def rmdir(self, name: str) -> str:
        """Remove an empty directory."""
        success, message = self.vfs.rmdir(name)

        if not success:
            if "Directory not empty" in message:
                raise OSError(message)

            if "Not a directory" in message:
                raise NotADirectoryError(message)

            raise FileNotFoundError(message)

        return message
    def touch(self, filename: str) -> str:
        """
        Create an empty file or update its timestamp.
        Raises error if file is actually a directory.
        """
        success, msg = self.vfs.touch(filename)
        
        if not success:
            raise FileExistsError(msg)
        
        return msg

    def cat(self, filename: str) -> str:
        """
        Display file contents.
        Raises FileNotFoundError if file doesn't exist.
        Raises IsADirectoryError if filename is a directory.
        """
        success, content = self.vfs.cat(filename)
        
        if not success:
            if "no such file or directory" in content:
                raise FileNotFoundError(content)
            if "is a directory" in content:
                raise IsADirectoryError(content)
            raise FileNotFoundError(content)
        
        return content
    def write(self, filename: str, content: str) -> str:
        """
        Write content to a file.

        Creates the file if it does not exist.
        Replaces existing file content if it exists.
        """
        if not filename:
            raise ValueError("write: filename cannot be empty")

        success, message = self.vfs.echo(content, filename)

        if not success:
            if "is a directory" in message:
                raise IsADirectoryError(message)

            raise FileNotFoundError(message)

        return message
    def append(self, filename: str, content: str) -> str:
        """
        Append content to a file.

        Raises FileNotFoundError if the file doesn't exist.
        Raises IsADirectoryError if the path is a directory.
        """
        if not filename:
            raise ValueError("append: filename cannot be empty")

        success, existing_content = self.vfs.cat(filename)

        if not success:
            if "is a directory" in existing_content:
                raise IsADirectoryError(existing_content)

            raise FileNotFoundError(existing_content)

        new_content = existing_content

        if new_content:
            new_content += "\n"

        new_content += content

        success, message = self.vfs.echo(
            content=new_content,
            filename=filename,
        )

        if not success:
            if "is a directory" in message:
                raise IsADirectoryError(message)

            raise FileNotFoundError(message)

        return message
    def echo(self, content: str, filename: str = None) -> str:
        """
        Print content or write to file.
        Returns the content that was printed/written.
        """
        success, msg = self.vfs.echo(content, filename)
        
        if not success:
            raise IsADirectoryError(msg)
        
        if filename:
            return msg
        return content

    def rm(self, name: str, recursive: bool = False) -> str:
        """
        Delete a file or directory.
        Raises FileNotFoundError if file doesn't exist.
        Raises IsADirectoryError if trying to delete directory without recursive.
        """
        success, msg = self.vfs.rm(name, recursive)
        
        if not success:
            if "no such file or directory" in msg:
                raise FileNotFoundError(msg)
            if "is a directory" in msg:
                raise IsADirectoryError(msg)
            raise FileNotFoundError(msg)
        
        return msg

    def cp(self, source: str, dest: str, recursive: bool = False) -> str:
        """
        Copy a file or directory.
        Raises FileNotFoundError if source doesn't exist.
        Raises IsADirectoryError if trying to copy directory without recursive.
        """
        success, msg = self.vfs.cp(source, dest, recursive)
        
        if not success:
            if "no such file or directory" in msg:
                raise FileNotFoundError(msg)
            if "is a directory" in msg:
                raise IsADirectoryError(msg)
            raise FileExistsError(msg)
        
        return msg

    def mv(self, source: str, dest: str) -> str:
        """
        Move or rename a file or directory.
        Raises FileNotFoundError if source doesn't exist.
        Raises FileExistsError if destination already exists.
        """
        success, msg = self.vfs.mv(source, dest)
        
        if not success:
            if "no such file or directory" in msg:
                raise FileNotFoundError(msg)
            if "already exists" in msg:
                raise FileExistsError(msg)
            raise FileNotFoundError(msg)
        
        return msg
    def _rename_command(self, arguments: list[str]) -> None:
        """Rename a file or directory."""
        if len(arguments) != 2:
            print("rename: usage: rename old_name new_name")
            return

        old_name = arguments[0]
        new_name = arguments[1]

        try:
            self.file_manager.mv(old_name, new_name)
            print(f"Renamed: {old_name} -> {new_name}")

        except FileNotFoundError as error:
            print(error)

        except FileExistsError as error:
            print(error)

        except PermissionError:
            print(f"rename: permission denied: {old_name}")