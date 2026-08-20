"""
Command dispatcher for Punas Power Shell.
"""

from collections.abc import Callable


CommandFunction = Callable[[list[str]], None]


class CommandDispatcher:
    """Register and execute shell commands."""

    def __init__(self) -> None:
        """Initialize the command registry."""
        self._commands: dict[str, CommandFunction] = {}

    def register(
        self,
        name: str,
        function: CommandFunction,
        aliases: list[str] | None = None,
    ) -> None:
        """Register a command and its optional aliases."""
        self._commands[name] = function

        if aliases:
            for alias in aliases:
                self._commands[alias] = function

    def execute(self, name: str, arguments: list[str]) -> bool:
        """
        Execute a registered command.

        Returns:
            True if the command exists and was executed.
            False if the command does not exist.
        """
        function = self._commands.get(name)

        if function is None:
            return False

        function(arguments)
        return True

    def get_commands(self) -> list[str]:
        """Return registered command names."""
        return sorted(self._commands)