"""
Core shell engine for Punas Power Shell (PPS).
"""

from typing import Final

from src.commands import CommandDispatcher
from src.filesystem import FileManager
from src.parser import CommandParser
from src.history import CommandHistory
from src.logger import Logger
from src.config import Config
class PunasShell:
    """Core interactive shell for PPS."""

    VERSION: Final[str] = "1.0.0"
    PROMPT: Final[str] = "psh> "
    def get_prompt(self) -> str:
        """Return the PPS shell prompt using the current directory."""
        current_directory = self.file_manager.pwd()
        
        if current_directory == "/":
            return "psh> "
        
        # Remove leading / and format nicely
        parts = current_directory.strip("/").split("/")
        
        return f"psh\\{'\\'.join(parts)}> "
    def __init__(self) -> None:
        """Initialize the shell."""
        self.running = False

        self.parser = CommandParser()
        self.dispatcher = CommandDispatcher()
        self.file_manager = FileManager()
        self.history = CommandHistory()
        self.config = Config()
        self.logger = Logger(log_file=self.config.get("log_file", "shell.log"))

        self._register_commands()
    def _cd_command(self, arguments: list[str]) -> None:
        """Change the current working directory."""
        if len(arguments) != 1:
            print("cd: expected exactly one directory")
            return

        try:
            self.file_manager.cd(arguments[0])
        except FileNotFoundError as error:
            print(error)
        except NotADirectoryError as error:
            print(error)
        except PermissionError:
            print(f"cd: permission denied: {arguments[0]}")
    def _register_commands(self) -> None:
        """Register commands available to the shell."""

        self.dispatcher.register(
            "exit",
            self._exit_command,
            aliases=["quit"],
        )

        self.dispatcher.register(
            "help",
            self._help_command,
        )

        self.dispatcher.register(
            "pwd",
            self._pwd_command,
        )

        self.dispatcher.register(
            "ls",
            self._ls_command,
            aliases=["dir"],
        )

        self.dispatcher.register(
            "cd",
            self._cd_command,
        )

        self.dispatcher.register(
            "mkdir",
            self._mkdir_command,
        )

        self.dispatcher.register(
            "touch",
            self._touch_command,
        )

        self.dispatcher.register(
            "rm",
            self._rm_command,
        )

        self.dispatcher.register(
            "cat",
            self._cat_command,
        )

        self.dispatcher.register(
            "echo",
            self._echo_command,
        )

        self.dispatcher.register(
            "cp",
            self._cp_command,
        )

        self.dispatcher.register(
            "mv",
            self._mv_command,
        )

        self.dispatcher.register(
            "history",
            self._history_command,
        )

        self.dispatcher.register(
            "config",
            self._config_command,
        )

        # Register extra commands from commands.txt (implemented or safe stubs)
        try:
            from src import extra_commands
            extra_commands.register_all(self.dispatcher, self)
        except Exception:
            # If extra_commands fails to load, continue without it
            pass

    def display_banner(self) -> None:
        """Display the PPS startup banner."""
        print("=" * 58)
        print("             PUNAS POWER SHELL (PPS)")
        print(f"                    Version {self.VERSION}")
        print("=" * 58)
        print()
        print("Launching Punas Shell...")
        print('Type "help" to get started.')
        print()
    def _pwd_command(self, arguments: list[str]) -> None:
        """Display the current working directory."""
        if arguments:
            print("pwd: too many arguments")
            return

        print(self.file_manager.pwd())
    def _ls_command(self, arguments: list[str]) -> None:
        """List files and directories."""
        if arguments:
            print("ls: arguments are not supported yet")
            return

        items = self.file_manager.ls()

        for name, item_type in items:
            if item_type == "dir":
                print(f"[DIR]  {name}")
            else:
                print(f"       {name}")

        print()
        print(f"Total files: {sum(1 for _, t in items if t == 'file')}")
    def _mkdir_command(self, arguments: list[str]) -> None:
        """Create a directory."""
        if len(arguments) != 1:
            print("mkdir: expected exactly one directory name")
            return

        try:
            self.file_manager.mkdir(arguments[0])
            print(f"Directory created: {arguments[0]}")
        except FileExistsError as error:
            print(error)
        except PermissionError:
            print(f"mkdir: permission denied: {arguments[0]}")

    def _touch_command(self, arguments: list[str]) -> None:
        """Create an empty file or update its timestamp."""
        if len(arguments) != 1:
            print("touch: expected exactly one filename")
            return

        try:
            self.file_manager.touch(arguments[0])
            print(f"File created: {arguments[0]}")
        except FileExistsError as error:
            print(error)
        except IsADirectoryError as error:
            print(error)
        except PermissionError:
            print(f"touch: permission denied: {arguments[0]}")

    def _rm_command(self, arguments: list[str]) -> None:
        """Delete a file or directory."""
        recursive = False
        name = None

        # Check for -r flag
        if len(arguments) == 2 and arguments[0] == "-r":
            recursive = True
            name = arguments[1]
        elif len(arguments) == 1:
            name = arguments[0]
        else:
            print("rm: usage: rm [-r] name")
            return

        try:
            self.file_manager.rm(name, recursive)
            print(f"Removed: {name}")
        except FileNotFoundError as error:
            print(error)
        except IsADirectoryError as error:
            print(error)
        except PermissionError:
            print(f"rm: permission denied: {name}")

    def _cat_command(self, arguments: list[str]) -> None:
        """Display file contents."""
        if len(arguments) != 1:
            print("cat: expected exactly one filename")
            return

        try:
            content = self.file_manager.cat(arguments[0])
            print(content)
        except FileNotFoundError as error:
            print(error)
        except IsADirectoryError as error:
            print(error)
        except PermissionError:
            print(f"cat: permission denied: {arguments[0]}")

    def _echo_command(self, arguments: list[str]) -> None:
        """Print text or write to file."""
        if len(arguments) == 0:
            print("")
            return

        # Check for redirection with >
        if ">" in arguments:
            redirect_index = arguments.index(">")
            text = " ".join(arguments[:redirect_index])
            
            if redirect_index + 1 >= len(arguments):
                print("echo: syntax error - no file after >")
                return
            
            filename = arguments[redirect_index + 1]
            
            try:
                self.file_manager.echo(text, filename)
                print(f"Written to {filename}")
            except IsADirectoryError as error:
                print(error)
            except PermissionError:
                print(f"echo: permission denied: {filename}")
        else:
            # Just print the text
            text = " ".join(arguments)
            print(text)

    def _cp_command(self, arguments: list[str]) -> None:
        """Copy a file or directory."""
        recursive = False
        source = None
        dest = None

        # Check for -r flag
        if len(arguments) == 3 and arguments[0] == "-r":
            recursive = True
            source = arguments[1]
            dest = arguments[2]
        elif len(arguments) == 2:
            source = arguments[0]
            dest = arguments[1]
        else:
            print("cp: usage: cp [-r] source destination")
            return

        try:
            self.file_manager.cp(source, dest, recursive)
            print(f"Copied: {source} -> {dest}")
        except FileNotFoundError as error:
            print(error)
        except IsADirectoryError as error:
            print(error)
        except FileExistsError as error:
            print(error)
        except PermissionError:
            print(f"cp: permission denied")

    def _mv_command(self, arguments: list[str]) -> None:
        """Move or rename a file or directory."""
        if len(arguments) != 2:
            print("mv: usage: mv source destination")
            return

        source = arguments[0]
        dest = arguments[1]

        try:
            self.file_manager.mv(source, dest)
            print(f"Moved: {source} -> {dest}")
        except FileNotFoundError as error:
            print(error)
        except FileExistsError as error:
            print(error)
        except PermissionError:
            print(f"mv: permission denied")

    def _history_command(self, arguments: list[str]) -> None:
        """Display command history."""
        if arguments and arguments[0] == "-c":
            # Clear history
            self.history.clear()
            print("History cleared")
            return

        if arguments and arguments[0] == "-s":
            # Search history
            if len(arguments) < 2:
                print("history -s: pattern required")
                return
            
            pattern = " ".join(arguments[1:])
            results = self.history.search(pattern)
            
            if not results:
                print(f"No history entries matching '{pattern}'")
                return
            
            print(f"History entries matching '{pattern}':")
            for i, entry in enumerate(results, 1):
                print(f"  {i}. {entry}")
            return

        # Show all or recent history
        limit = 20  # Default to show last 20
        if arguments and arguments[0].isdigit():
            limit = int(arguments[0])

        entries = self.history.get_recent(limit)
        
        if not entries:
            print("No history")
            return

        for i, entry in enumerate(entries, 1):
            print(f"  {i}. {entry}")

    def _config_command(self, arguments: list[str]) -> None:
        """Manage shell configuration."""
        if not arguments:
            # Show all config
            print("\nCurrent Configuration:")
            for key, value in self.config.get_all().items():
                print(f"  {key}: {value}")
            return

        if arguments[0] == "get":
            if len(arguments) < 2:
                print("config get: key required")
                return
            
            key = arguments[1]
            value = self.config.get(key)
            
            if value is None:
                print(f"config: unknown setting '{key}'")
            else:
                print(f"{key}: {value}")
            return

        if arguments[0] == "set":
            if len(arguments) < 3:
                print("config set: key and value required")
                return
            
            key = arguments[1]
            value = arguments[2]
            
            # Try to convert to appropriate type
            if value.lower() in ("true", "false"):
                value = value.lower() == "true"
            elif value.isdigit():
                value = int(value)
            
            self.config.set(key, value)
            print(f"Configuration updated: {key} = {value}")
            return

        if arguments[0] == "reset":
            self.config.reset_to_defaults()
            print("Configuration reset to defaults")
            return

        print("config: usage: config [get key | set key value | reset]")
    def start(self) -> None:
        """Start the interactive shell."""
        self.running = True
        self.logger.session_start()
        self.display_banner()
        self.run()

    def run(self) -> None:
        """Run the main shell loop."""
        while self.running:
            try:
                command_line = input(self.get_prompt())
                self.process_input(command_line)

            except KeyboardInterrupt:
                print()
                print("Use 'exit' to leave Punas Shell.")

            except EOFError:
                print()
                self.stop()
    def process_input(self, command_line: str) -> None:
        """Parse and execute a command."""
        try:
            parsed = self.parser.parse(command_line)

            if parsed is None:
                return

            # Track in history
            executed = self.dispatcher.execute(
                parsed.name,
                parsed.arguments,
            )
            
            # Add to history and log
            if command_line.strip():
                self.history.add(command_line, success=executed)
                self.logger.command(command_line, success=executed)

            if not executed:
                print(f'Unknown command: "{parsed.name}"')
                print('Type "help" to see available commands.')
                self.logger.error(f"Unknown command: {parsed.name}")

        except ValueError as error:
            print(error)
            if command_line.strip():
                self.history.add(command_line, success=False)
                self.logger.error(str(error))

        except Exception as error:
            print(f"Error: {error}")
            if command_line.strip():
                self.history.add(command_line, success=False)
                self.logger.error(str(error))

    def _help_command(self, arguments: list[str]) -> None:
        """Display currently registered commands."""
        print()
        print("Available commands:")
        print()

        for command in self.dispatcher.get_commands():
            print(f"  {command}")

        print()

    def _exit_command(self, arguments: list[str]) -> None:
        """Exit Punas Shell."""
        self.stop()

    def stop(self) -> None:
        """Stop the shell."""
        print()
        print("Shutting down Punas Shell...")
        print("Goodbye!")
        self.logger.session_end()

        self.running = False