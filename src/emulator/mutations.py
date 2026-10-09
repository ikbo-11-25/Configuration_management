"""Removal and ownership changes restricted to memory nodes."""

import re

from emulator.options import CommandError, parse_flags
from emulator.vfs import MissingPath

MIN_CHOWN_OPERANDS = 2
IDENTITY_PATTERN = re.compile(r"[\w.-]+\Z")


def parse_owner(value: str):
    """Validate a virtual OWNER or OWNER:GROUP specification."""
    owner, separator, group = value.partition(":")
    if not IDENTITY_PATTERN.fullmatch(owner):
        raise CommandError("invalid owner; expected OWNER[:GROUP]")
    if separator and not IDENTITY_PATTERN.fullmatch(group):
        raise CommandError("invalid group; expected OWNER:GROUP")
    return owner, group if separator else None


class MutationCommands:
    """Implement rm and chown without invoking physical operations."""

    def __init__(self, shell) -> None:
        """Retain shell state and its isolated VFS snapshot."""
        self.shell = shell

    def rm(self, args: list[str]) -> str:
        """Remove files, or recursively remove directories with -r/-R."""
        flags, paths = parse_flags(args, "rfR")
        if not paths and "f" not in flags:
            raise CommandError("missing operand")
        recursive = bool(flags & {"r", "R"})
        for path in paths:
            try:
                self.remove_one(path, recursive)
            except MissingPath:
                if "f" not in flags:
                    raise
        return ""

    def remove_one(self, path: str, recursive: bool) -> None:
        """Delete a memory child, protecting root and active directories."""
        if path.rstrip("/").split("/")[-1] in (".", ".."):
            raise CommandError("refusing to remove . or ..")
        canonical, node = self.shell.vfs.get(path, self.shell.cwd)
        if canonical == "/":
            raise CommandError("refusing to remove VFS root")
        cwd = self.shell.cwd
        if cwd == canonical or cwd.startswith(canonical + "/"):
            raise CommandError("refusing to remove current directory/ancestor")
        if node.is_dir and not recursive:
            raise CommandError(f"is a directory (use -r): {path}")
        parent_path, _, name = canonical.rpartition("/")
        parent = self.shell.vfs.get(parent_path or "/")[1]
        del parent.children[name]

    def chown(self, args: list[str]) -> str:
        """Change virtual owner/group, optionally for all descendants."""
        flags, operands = parse_flags(args, "R")
        if len(operands) < MIN_CHOWN_OPERANDS:
            raise CommandError("usage: chown [-R] OWNER[:GROUP] PATH ...")
        owner, group = parse_owner(operands[0])
        for path in operands[1:]:
            node = self.shell.vfs.get(path, self.shell.cwd)[1]
            nodes = self.shell.vfs.walk(node) if "R" in flags else [node]
            for current in nodes:
                current.owner = owner
                if group is not None:
                    current.group = group
        return ""
