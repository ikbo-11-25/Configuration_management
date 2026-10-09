"""Verify every supported rm/chown mode and physical isolation."""

import unittest
from unittest.mock import patch

from emulator.config import PROJECT_ROOT
from emulator.shell import Shell
from emulator.vfs import MissingPath, Node, VFS


class MutationTests(unittest.TestCase):
    """Use a fresh snapshot for each mutation test."""

    def setUp(self):
        """Load physical example files without changing them."""
        self.source = PROJECT_ROOT / "examples" / "vfs" / "deep"
        self.shell = Shell(vfs=VFS.from_directory(self.source))

    def test_rm_file(self):
        """A removed virtual file disappears only from memory."""
        self.assertFalse(self.shell.execute("rm hello.txt").error)
        with self.assertRaises(MissingPath):
            self.shell.vfs.get("hello.txt")
        self.assertTrue((self.source / "hello.txt").exists())

    def test_rm_recursive(self):
        """Both recursive flags delete directory trees."""
        self.assertTrue(self.shell.execute("rm docs").error)
        self.assertFalse(self.shell.execute("rm -r docs").error)
        self.assertFalse(self.shell.execute("rm -R tmp").error)
        self.assertNotIn("docs", self.shell.vfs.root.children)

    def test_rm_force(self):
        """Force ignores missing operands but not invalid options/types."""
        for line in ("rm -f absent", "rm -rf absent", "rm -f"):
            self.assertFalse(self.shell.execute(line).error)
        for line in ("rm absent", "rm", "rm -f docs", "rm -z hello.txt"):
            self.assertTrue(self.shell.execute(line).error)

    def test_rm_protected_paths(self):
        """Root, dot, parent, and current ancestors are protected."""
        self.shell.execute("cd /docs/course/tasks")
        paths = ("/", ".", "..", "/docs", "/docs/course/tasks")
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue(self.shell.execute(f"rm -rf {path}").error)
        self.assertFalse(self.shell.execute("ls").error)

    def test_rm_multiple_and_double_dash(self):
        """Multiple paths and names beginning with - can be removed."""
        self.shell.vfs.root.children["-file"] = Node("-file", False)
        self.assertFalse(self.shell.execute("rm -- -file .hidden").error)
        self.assertFalse(self.shell.execute("rm hello.txt tmp/cache.txt").error)
        self.assertNotIn("-file", self.shell.vfs.root.children)

    def test_chown_owner_and_group(self):
        """An owner-only change preserves the group."""
        node = self.shell.vfs.get("hello.txt")[1]
        self.shell.execute("chown alice hello.txt")
        self.assertEqual((node.owner, node.group), ("alice", "users"))
        self.shell.execute("chown bob:staff hello.txt .hidden")
        self.assertEqual((node.owner, node.group), ("bob", "staff"))
        self.assertEqual(self.shell.vfs.get(".hidden")[1].owner, "bob")

    def test_chown_recursive(self):
        """Recursive ownership updates every file and directory."""
        self.shell.execute("chown -R student:course docs")
        docs = self.shell.vfs.get("docs")[1]
        for node in self.shell.vfs.walk(docs):
            self.assertEqual((node.owner, node.group), ("student", "course"))
        self.assertIn("student course", self.shell.execute(
            "ls -l docs/course/tasks").output)

    def test_chown_nonrecursive(self):
        """Changing a directory alone leaves descendants intact."""
        descendant = self.shell.vfs.get("docs/readme.txt")[1]
        original = descendant.owner
        self.shell.execute("chown other docs")
        self.assertEqual(descendant.owner, original)
        self.assertEqual(self.shell.vfs.get("docs")[1].owner, "other")

    def test_chown_errors(self):
        """Malformed identities, paths, flags, and arity are rejected."""
        lines = ("chown", "chown alice", "chown alice absent",
                 "chown user: hello.txt", "chown :group hello.txt",
                 "chown a:b:c hello.txt", "chown -z alice hello.txt")
        original = self.shell.vfs.get("hello.txt")[1].owner
        for line in lines:
            with self.subTest(line=line):
                self.assertTrue(self.shell.execute(line).error)
                self.assertEqual(self.shell.vfs.get("hello.txt")[1].owner,
                                 original)

    def test_physical_tree_unchanged(self):
        """Data, directories, timestamps, and host ownership stay intact."""
        def snapshot():
            """Record source structure, bytes, and physical metadata."""
            items = {}
            for path in self.source.rglob("*"):
                data = path.read_bytes() if path.is_file() else None
                info = path.stat()
                items[str(path.relative_to(self.source))] = (
                    data, info.st_mtime_ns, info.st_mode,
                    info.st_uid, info.st_gid,
                )
            return items
        before = snapshot()
        with patch("pathlib.Path.unlink", side_effect=AssertionError), \
                patch("os.chown", create=True, side_effect=AssertionError):
            self.assertFalse(self.shell.execute("chown -R a:b /").error)
            self.assertFalse(self.shell.execute("rm -r docs tmp").error)
        self.assertEqual(snapshot(), before)


if __name__ == "__main__":
    unittest.main()
