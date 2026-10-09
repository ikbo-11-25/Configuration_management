"""Widget smoke test for the actual Tkinter interface."""

import getpass
import socket
import tkinter as tk
import unittest

from emulator.gui import Terminal
from emulator.shell import Shell


class GuiTests(unittest.TestCase):
    """Check command input and the real operating-system window title."""

    def test_title_input_and_error(self):
        """Create actual widgets and execute an unknown command."""
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"graphical display unavailable: {error}")
        root.withdraw()
        try:
            terminal = Terminal(root, Shell())
            identity = f"{getpass.getuser()}@{socket.gethostname()}"
            self.assertEqual(root.title(), f"Эмулятор - [{identity}]")
            terminal.entry.insert(0, "unknown")
            terminal.submit()
            output = terminal.output.get("1.0", "end")
            self.assertIn("/ $ unknown", output)
            self.assertIn("unknown: command not found", output)
            self.assertEqual(terminal.entry.get(), "")
            self.assertEqual(str(terminal.output.cget("state")), "disabled")
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
