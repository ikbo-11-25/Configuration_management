"""Tests for the first-stage command loop."""

import unittest

from emulator.parser import parse_command
from emulator.shell import Shell


class ReplTests(unittest.TestCase):
    """Check parsing, dispatch, blank input, and exit."""

    def test_whitespace(self):
        """Whitespace separates the command and arguments."""
        self.assertEqual(parse_command("  ls\t/a  /b "),
                         ["ls", "/a", "/b"])

    def test_empty_input(self):
        """An empty line is a successful no-op."""
        result = Shell().execute(" ")
        self.assertEqual(result.output, "")
        self.assertFalse(result.error)

    def test_unknown_command(self):
        """Unknown commands return an error without ending the shell."""
        result = Shell().execute("missing")
        self.assertTrue(result.error)
        self.assertFalse(result.exit_requested)

    def test_exit(self):
        """Exit only accepts an empty argument list."""
        self.assertTrue(Shell().execute("exit").exit_requested)
        self.assertTrue(Shell().execute("exit extra").error)

    def test_empty_vfs(self):
        """An empty memory VFS still supports ls and cd."""
        self.assertEqual(Shell().execute("ls").output, "")
        self.assertFalse(Shell().execute("cd /").error)


if __name__ == "__main__":
    unittest.main()
