"""Tests for directory loading and virtual path resolution."""

import unittest
from pathlib import Path

from emulator.config import PROJECT_ROOT
from emulator.vfs import VFS, VFSError
from support import temporary_directory


class VfsTests(unittest.TestCase):
    """Ensure snapshots are isolated from the physical filesystem."""

    def prepare_fixture(self):
        """Load the three-level example before each check."""
        self.source = PROJECT_ROOT / "examples" / "vfs" / "deep"
        self.vfs = VFS.from_directory(self.source)

    def test_nested_content(self):
        """Nested paths expose the original file bytes."""
        self.prepare_fixture()
        path, node = self.vfs.get("/docs/course/tasks/task.txt")
        self.assertEqual(path, "/docs/course/tasks/task.txt")
        self.assertFalse(node.is_dir)
        self.assertIn(b"Level three", node.data)

    def test_relative_paths(self):
        """Resolve relative, dot, parent, and repeated slash paths."""
        self.prepare_fixture()
        path, node = self.vfs.get("../course//tasks/.", "/docs/course")
        self.assertEqual(path, "/docs/course/tasks")
        self.assertTrue(node.is_dir)
        self.assertEqual(self.vfs.get("../../..", "/")[0], "/")

    def test_invalid_paths(self):
        """Missing entries and file traversal produce clear errors."""
        self.prepare_fixture()
        paths = ["missing", "hello.txt/child", "hello.txt/..",
                 "hello.txt/", "", "\x00"]
        for path in paths:
            with self.subTest(path=path), self.assertRaises(VFSError):
                self.vfs.get(path)

    def test_bad_sources(self):
        """A missing source or a file cannot be used as a VFS root."""
        self.prepare_fixture()
        for path in (self.source / "missing", self.source / "hello.txt"):
            with self.subTest(path=path), self.assertRaises(VFSError):
                VFS.from_directory(path)

    def test_bytes_are_a_snapshot(self):
        """Later physical changes cannot affect loaded bytes."""
        self.prepare_fixture()
        with temporary_directory() as directory:
            source = Path(directory)
            file = source / "binary.dat"
            file.write_bytes(b"\x00\xfforiginal")
            vfs = VFS.from_directory(source)
            file.write_bytes(b"changed")
            self.assertEqual(vfs.get("binary.dat")[1].data,
                             b"\x00\xfforiginal")

    def test_independent_snapshots(self):
        """Editing a memory node cannot alter another loaded snapshot."""
        self.prepare_fixture()
        other = VFS.from_directory(self.source)
        self.vfs.get("hello.txt")[1].data = b"edited"
        self.assertNotEqual(other.get("hello.txt")[1].data, b"edited")


if __name__ == "__main__":
    unittest.main()
