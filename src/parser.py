"""
Command parser for Punas Power Shell.
"""

import shlex
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    """Represents a parsed shell command."""

    name: str
    arguments: list[str]


class CommandParser:
    """Parses user input into a command and its arguments."""

    def parse(self, command_line: str) -> ParsedCommand | None:
        """
        Parse a command line.

        Example:
            mkdir Projects

        becomes:
            name = "mkdir"
            arguments = ["Projects"]
        """
        command_line = command_line.strip()

        if not command_line:
            return None

        try:
            parts = shlex.split(command_line)
        except ValueError as error:
            raise ValueError(f"Parser error: {error}") from error

        if not parts:
            return None

        return ParsedCommand(
            name=parts[0].lower(),
            arguments=parts[1:],
        )