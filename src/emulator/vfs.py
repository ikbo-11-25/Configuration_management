"""Read a physical directory once, then operate on memory nodes only."""

import getpass
import stat
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


class VFSError(ValueError):
    """A virtual path or physical VFS source is invalid."""


class MissingPath(VFSError):
    """A virtual file or directory does not exist."""


@dataclass
class Node:
    """A directory or file, including emulated ownership metadata."""

    name: str
    is_dir: bool
    data: bytes = b""
    children: dict[str, "Node"] = field(default_factory=dict)
    owner: str = field(default_factory=getpass.getuser)
    group: str = "users"
    modified: datetime = field(default_factory=datetime.now)


def check_source(path: Path) -> None:
    """Reject links and reparse points rather than follow external data."""
    info = path.lstat()
    attributes = getattr(info, "st_file_attributes", 0)
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    if stat.S_ISLNK(info.st_mode) or attributes & reparse:
        raise VFSError(f"symbolic links/junctions are not supported: {path}")
    if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
        raise VFSError(f"unsupported source entry: {path}")


class VFS:
    """Contain an isolated snapshot of a virtual directory tree."""

    def __init__(self) -> None:
        """Create an empty virtual root directory."""
        self.root = Node("/", True)

    @classmethod
    def from_directory(cls, source: Path) -> "VFS":
        """Copy file bytes and directory structure without writing to disk."""
        vfs = cls()
        try:
            check_source(source)
            if not source.is_dir():
                raise VFSError(f"not a directory: {source}")
            pending = [(source, vfs.root)]
            while pending:
                physical, parent = pending.pop()
                for path in sorted(physical.iterdir()):
                    check_source(path)
                    node = Node(path.name, path.is_dir())
                    node.modified = datetime.fromtimestamp(
                        path.stat().st_mtime,
                    )
                    parent.children[path.name] = node
                    if node.is_dir:
                        pending.append((path, node))
                    else:
                        node.data = path.read_bytes()
        except OSError as error:
            raise VFSError(f"cannot load {source}: {error}") from error
        return vfs

    def get(self, path: str, cwd: str = "/") -> tuple[str, Node]:
        """Resolve UNIX absolute/relative paths, dot, and parent segments."""
        if not path or "\x00" in path:
            raise VFSError("invalid empty path or NUL character")
        parts = [] if path.startswith("/") else cwd.strip("/").split("/")
        parts = [part for part in parts if part]
        node = self._lookup(parts)
        for part in path.split("/"):
            if not part:
                continue
            parts, node = self._step(parts, node, part)
        if path.endswith("/") and not node.is_dir:
            raise VFSError(f"not a directory: {path}")
        return "/" + "/".join(parts), node

    def _step(self, parts: list[str], node: Node, part: str):
        """Advance one path segment, enforcing directory traversal."""
        if not node.is_dir:
            raise VFSError(f"not a directory: /{'/'.join(parts)}")
        if part == ".":
            return parts, node
        if part == "..":
            parts = parts[:-1]
        else:
            parts = parts + [part]
        return parts, self._lookup(parts)

    def _lookup(self, parts: list[str]) -> Node:
        """Find a node using canonical path components."""
        node = self.root
        for part in parts:
            if not node.is_dir:
                raise VFSError(f"not a directory: {part}")
            if part not in node.children:
                joined = "/" + "/".join(parts)
                raise MissingPath(f"no such file or directory: {joined}")
            node = node.children[part]
        return node

    def walk(self, node: Node):
        """Yield a node and all descendants, without recursive calls."""
        pending = [node]
        while pending:
            current = pending.pop()
            yield current
            pending.extend(current.children.values())
