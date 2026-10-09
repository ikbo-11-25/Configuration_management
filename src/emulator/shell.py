"""Command dispatch and shell state."""

from dataclasses import dataclass

from emulator.config import Config
from emulator.parser import parse_command
from emulator.vfs import VFS


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
        self.config = config or Config()
        self.vfs = vfs or VFS()
        self.handlers = {
            "ls": self.stub, "cd": self.stub,
            "conf-dump": self.conf_dump,
        }

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
        return handler(command, args)

    def stub(self, command: str, args: list[str]) -> Result:
        """Show the command and arguments in the REPL prototype."""
        return Result(f"{command}: {args!r}")

    def conf_dump(self, command: str, args: list[str]) -> Result:
        """Print configured paths and interface settings."""
        if args:
            return Result(f"{command}: arguments are not supported", True)
        return Result(self.config.dump())
