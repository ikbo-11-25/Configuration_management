"""Tests for listing, navigation, calendars, and session identity."""

import getpass
import socket
import unittest

from emulator.config import PROJECT_ROOT
from emulator.shell import Shell
from emulator.vfs import VFS


class CommandTests(unittest.TestCase):
    """Check supported command modes and errors."""

    def setUp(self):
        """Load a fresh VFS for every test."""
        source = PROJECT_ROOT / "examples" / "vfs" / "deep"
        self.shell = Shell(vfs=VFS.from_directory(source))

    def test_ls_modes(self):
        """Hidden files, details, and multiple operands work."""
        self.assertNotIn(".hidden", self.shell.execute("ls").output)
        self.assertIn(".hidden", self.shell.execute("ls -a").output)
        detailed = self.shell.execute("ls -al").output
        self.assertIn(getpass.getuser(), detailed)
        self.assertIn("drwxr-xr-x", detailed)
        self.assertIn("docs:", self.shell.execute("ls docs tmp").output)
        self.assertEqual(self.shell.execute("ls -- hello.txt").output,
                         "hello.txt")

    def test_ls_errors(self):
        """Unsupported flags and nonexistent paths are errors."""
        for line in ("ls missing", "ls -z", "ls hello.txt/"):
            with self.subTest(line=line):
                self.assertTrue(self.shell.execute(line).error)

    def test_cd_modes(self):
        """Relative paths, root defaults, and previous directory work."""
        self.assertFalse(self.shell.execute("cd /docs/course/tasks").error)
        self.assertEqual(self.shell.cwd, "/docs/course/tasks")
        self.shell.execute("cd ../..")
        self.assertEqual(self.shell.cwd, "/docs")
        self.assertEqual(self.shell.execute("cd -").output,
                         "/docs/course/tasks")
        self.shell.execute("cd")
        self.assertEqual(self.shell.cwd, "/")
        self.shell.execute("cd ../../..")
        self.assertEqual(self.shell.cwd, "/")

    def test_cd_errors_preserve_cwd(self):
        """An invalid cd does not change directory state."""
        self.shell.execute("cd docs")
        for line in ("cd missing", "cd /hello.txt", "cd / /docs"):
            with self.subTest(line=line):
                self.assertTrue(self.shell.execute(line).error)
                self.assertEqual(self.shell.cwd, "/docs")

    def test_cal_leap_year(self):
        """February 2024 includes the leap day and Sunday-first header."""
        output = self.shell.execute("cal 2 2024").output
        self.assertIn("February 2024", output)
        self.assertIn("29", output)
        self.assertIn("Su Mo Tu We Th Fr Sa", output)

    def test_cal_year_and_current(self):
        """Year, -y, and the current month are supported."""
        for line in ("cal 2026", "cal -y 2026"):
            output = self.shell.execute(line).output
            self.assertIn("January", output)
            self.assertIn("December", output)
        self.assertFalse(self.shell.execute("cal").error)
        self.assertFalse(self.shell.execute("cal -y").error)

    def test_cal_errors(self):
        """Invalid numbers, bounds, flags, and arity produce errors."""
        lines = ("cal 13 2026", "cal 0 2026", "cal x", "cal 0",
                 "cal 10000", "cal 1 2 3", "cal -y 2 2026", "cal -z")
        for line in lines:
            with self.subTest(line=line):
                self.assertTrue(self.shell.execute(line).error)

    def test_who(self):
        """Who exposes real host identity for the current session."""
        output = self.shell.execute("who").output
        self.assertIn(getpass.getuser(), output)
        self.assertIn(socket.gethostname(), output)
        self.assertIn("emulator", output)
        self.assertTrue(self.shell.execute("who extra").error)


if __name__ == "__main__":
    unittest.main()
