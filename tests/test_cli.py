"""Application-level tests with real startup scripts and exit codes."""

import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

from emulator.__main__ import main
from emulator.config import PROJECT_ROOT


class CliTests(unittest.TestCase):
    """Check the complete loader, dispatcher, and script runner together."""

    def invoke(self, arguments):
        """Capture a headless application invocation."""
        output = StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            status = main(arguments)
        return status, output.getvalue()

    def test_success_script(self):
        """All commands complete successfully in the end-to-end script."""
        script = PROJECT_ROOT / "examples" / "scripts" / "success.txt"
        status, output = self.invoke(["--headless", "--startup", str(script)])
        self.assertEqual(status, 0)
        self.assertIn("student course", output)
        self.assertIn("/ $ exit", output)

    def test_error_scripts(self):
        """Every deliberate-error script returns code 1 and stops."""
        scripts = PROJECT_ROOT / "examples" / "scripts"
        names = ("stage2-error.txt", "stage3.txt", "stage4.txt",
                 "stage4-cal-error.txt", "stage4-ls-error.txt",
                 "stage5.txt", "stage5-chown-error.txt",
                 "stage5-rm-error.txt")
        for name in names:
            with self.subTest(name=name):
                status, output = self.invoke([
                    "--headless", "--startup", str(scripts / name),
                ])
                self.assertEqual(status, 1)
                self.assertIn("startup: stopped at line", output)
                self.assertNotIn("THIS_LINE_MUST_NOT_RUN", output)

    def test_three_sources(self):
        """All demonstration sources load with all CLI parameters."""
        script = PROJECT_ROOT / "examples" / "scripts" / "stage2.txt"
        for name in ("minimal", "files", "deep"):
            with self.subTest(name=name):
                source = PROJECT_ROOT / "examples" / "vfs" / name
                status, output = self.invoke([
                    "--vfs", str(source), "--startup", str(script),
                    "--headless",
                ])
                self.assertEqual(status, 0)
                self.assertIn(f"vfs={source}", output)

    def test_missing_source(self):
        """Source errors fail before attempting script execution."""
        status, output = self.invoke([
            "--vfs", "nonexistent-source", "--startup", "none",
            "--headless",
        ])
        self.assertEqual(status, 1)
        self.assertIn("VFS:", output)


if __name__ == "__main__":
    unittest.main()
