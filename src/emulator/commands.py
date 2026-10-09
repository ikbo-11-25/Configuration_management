"""Read-only UNIX-like commands operating on the virtual filesystem."""

import calendar
import getpass
import socket
from datetime import date

from emulator.options import CommandError, parse_flags

MAX_CD_OPERANDS = 1
MAX_CAL_OPERANDS = 2
MIN_YEAR = 1
MAX_YEAR = 9999
MIN_MONTH = 1
MAX_MONTH = 12


def long_entry(name, node) -> str:
    """Format emulated mode, owner, group, size, date, and name."""
    mode = "drwxr-xr-x" if node.is_dir else "-rw-r--r--"
    size = 0 if node.is_dir else len(node.data)
    suffix = "/" if node.is_dir and name not in (".", "..") else ""
    return (f"{mode} 1 {node.owner} {node.group} {size:>6} "
            f"{node.modified:%Y-%m-%d %H:%M} {name}{suffix}")


class CoreCommands:
    """Implement ls, cd, cal, and who using shared shell state."""

    def __init__(self, shell) -> None:
        """Keep the shell state used by command handlers."""
        self.shell = shell

    def ls(self, args: list[str]) -> str:
        """List files or directory entries, with -a and -l modes."""
        flags, paths = parse_flags(args, "al")
        paths = paths or ["."]
        blocks = []
        for path in paths:
            canonical, node = self.shell.vfs.get(path, self.shell.cwd)
            entries = self.list_entries(canonical, node, "a" in flags)
            lines = []
            for name, entry in entries:
                if "l" in flags:
                    lines.append(long_entry(name, entry))
                else:
                    suffix = "/" if entry.is_dir else ""
                    lines.append(name + suffix)
            heading = f"{path}:\n" if len(paths) > MAX_CD_OPERANDS else ""
            blocks.append(heading + "\n".join(lines))
        return "\n\n".join(blocks)

    def list_entries(self, path, node, show_hidden):
        """Choose the listed node or visible children of a directory."""
        if not node.is_dir:
            return [(node.name, node)]
        entries = sorted(node.children.items())
        if not show_hidden:
            return [(name, entry) for name, entry in entries
                    if not name.startswith(".")]
        parent_path = path.rpartition("/")[0] or "/"
        parent = self.shell.vfs.get(parent_path)[1]
        return [(".", node), ("..", parent)] + entries

    def cd(self, args: list[str]) -> str:
        """Change directory; no operand selects / and - selects previous."""
        _, paths = parse_flags(args, "")
        if len(paths) > MAX_CD_OPERANDS:
            raise CommandError("expected at most one directory")
        path = paths[0] if paths else "/"
        show_path = path == "-"
        if show_path:
            path = self.shell.previous_cwd
        canonical, node = self.shell.vfs.get(path, self.shell.cwd)
        if not node.is_dir:
            raise CommandError(f"not a directory: {path}")
        self.shell.previous_cwd = self.shell.cwd
        self.shell.cwd = canonical
        return canonical if show_path else ""

    def cal(self, args: list[str]) -> str:
        """Print a current month, a month/year pair, or a whole year."""
        flags, values = parse_flags(args, "y")
        if len(values) > MAX_CAL_OPERANDS:
            raise CommandError("usage: cal [[month] year] | cal -y [year]")
        try:
            numbers = [int(value) for value in values]
        except ValueError as error:
            raise CommandError("month and year must be integers") from error
        today = date.today()
        whole_year = "y" in flags or len(numbers) == MAX_CD_OPERANDS
        if "y" in flags and len(numbers) > MAX_CD_OPERANDS:
            raise CommandError("usage: cal -y [year]")
        year = numbers[-1] if numbers else today.year
        if not MIN_YEAR <= year <= MAX_YEAR:
            raise CommandError(f"year must be {MIN_YEAR}..{MAX_YEAR}")
        renderer = calendar.TextCalendar(firstweekday=calendar.SUNDAY)
        if whole_year:
            return renderer.formatyear(year).rstrip()
        month = numbers[0] if numbers else today.month
        if not MIN_MONTH <= month <= MAX_MONTH:
            raise CommandError(f"month must be {MIN_MONTH}..{MAX_MONTH}")
        return renderer.formatmonth(year, month).rstrip()

    def who(self, args: list[str]) -> str:
        """Show the current emulator session using real host identity."""
        if args:
            raise CommandError("arguments are not supported")
        user = getpass.getuser()
        hostname = socket.gethostname()
        return (f"{user} emulator "
                f"{self.shell.started:%Y-%m-%d %H:%M} ({hostname})")
