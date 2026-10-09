"""Command dispatch and shell state."""

from dataclasses import dataclass
from datetime import datetime

from emulator.commands import CoreCommands
from emulator.config import Config
from emulator.options import CommandError
from emulator.parser import parse_command
from emulator.vfs import VFS, VFSError


@dataclass(frozen=True)
class Result:
    """Output and control flags returned by one command."""

    output: str = ""
    error: bool = False
    exit_requested: bool = False


class Shell:
    """Execute emulator commands without invoking the host shell."""

    def __init__(self, config: Config | None = None,
                 vfs: VFS | None = None) -> None:
        """Register commands implemented at this development stage."""
        self.cwd = "/"
        self.previous_cwd = "/"
        self.started = datetime.now()
        self.config = config or Config()
        self.vfs = vfs or VFS()
        core = CoreCommands(self)
        self.handlers = {"ls": core.ls, "cd": core.cd,
                         "cal": core.cal, "who": core.who,
                         "conf-dump": self.conf_dump}

    @property
    def prompt(self) -> str:
        """Return the prompt shown before user and script input."""
        return f"{self.cwd} $ "

    def execute(self, line: str) -> Result:
        """Parse a line and report unknown commands as errors."""
        words = parse_command(line)
        if not words:
            return Result()
        command, *args = words
        if command == "exit":
            if args:
                return Result("exit: arguments are not supported", True)
            return Result(exit_requested=True)
        handler = self.handlers.get(command)
        if handler is None:
            return Result(f"{command}: command not found", True)
        try:
            return Result(handler(args))
        except (CommandError, VFSError) as error:
            return Result(f"{command}: {error}", True)

    def conf_dump(self, args: list[str]) -> str:
        """Print configured paths and interface settings."""
        if args:
            raise CommandError("arguments are not supported")
        return self.config.dump()
