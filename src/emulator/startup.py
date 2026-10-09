"""Execution of UTF-8 scripts with transcript and stop-on-error."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from emulator.shell import Shell


@dataclass(frozen=True)
class ScriptStatus:
    """Tell the launcher whether a script failed or requested exit."""

    failed: bool = False
    exit_requested: bool = False


def run_script(shell: Shell, path: Path,
               write: Callable[[str], None]) -> ScriptStatus:
    """Show commands and results, halting at the first error or exit."""
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as error:
        write(f"startup: {error}")
        return ScriptStatus(failed=True)
    for number, line in enumerate(lines, start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        write(shell.prompt + line)
        result = shell.execute(line)
        if result.output:
            write(result.output)
        if result.error:
            write(f"startup: stopped at line {number}")
            return ScriptStatus(failed=True)
        if result.exit_requested:
            return ScriptStatus(exit_requested=True)
    return ScriptStatus()
