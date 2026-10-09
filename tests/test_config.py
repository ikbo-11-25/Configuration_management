"""Configuration and startup-script regression tests."""

import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from emulator.config import Config, parse_config
from emulator.shell import Shell
from emulator.startup import run_script
from support import temporary_directory


class ConfigTests(unittest.TestCase):
    """Verify options and key-value output."""

    def test_paths_with_spaces(self):
        """Argument parsing preserves quoted physical paths."""
        config = parse_config(["--vfs", "with space", "--startup", "a.txt"])
        self.assertEqual(config.vfs, Path("with space").resolve())
        self.assertEqual(config.startup, Path("a.txt").resolve())

    def test_invalid_options(self):
        """Unknown options and incomplete headless mode fail clearly."""
        for args in (["--unknown"], ["--headless"]):
            with self.subTest(args=args), redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    parse_config(args)
                self.assertEqual(caught.exception.code, 2)

    def test_dump(self):
        """The service command exposes every configured setting."""
        output = Shell(Config()).execute("conf-dump").output
        self.assertIn("vfs=", output)
        self.assertIn("startup=(none)", output)
        self.assertIn("headless=false", output)
        self.assertTrue(Shell().execute("conf-dump extra").error)


class StartupTests(unittest.TestCase):
    """Verify the transcript and immediate stop conditions."""

    def run_text(self, text):
        """Run a temporary script and return status and transcript."""
        with temporary_directory() as directory:
            script = Path(directory) / "script.txt"
            script.write_text(text, encoding="utf-8-sig")
            lines = []
            status = run_script(Shell(), script, lines.append)
        return status, "\n".join(lines)

    def test_stop_on_error(self):
        """The first failed command stops the rest of the script."""
        status, output = self.run_text("ls\nunknown\ncd sentinel")
        self.assertTrue(status.failed)
        self.assertIn("/ $ ls", output)
        self.assertIn("stopped at line 2", output)
        self.assertNotIn("sentinel", output)

    def test_stop_on_exit(self):
        """Exit skips all subsequent commands."""
        status, output = self.run_text("# comment\n\nexit\nls sentinel")
        self.assertTrue(status.exit_requested)
        self.assertFalse(status.failed)
        self.assertNotIn("sentinel", output)

    def test_missing_script(self):
        """Unreadable scripts are reported as errors."""
        lines = []
        status = run_script(Shell(), Path("missing-script"), lines.append)
        self.assertTrue(status.failed)
        self.assertIn("startup:", lines[0])


if __name__ == "__main__":
    unittest.main()
