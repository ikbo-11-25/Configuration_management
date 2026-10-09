"""Launch the graphical shell emulator."""

import tkinter as tk

from emulator.gui import Terminal
from emulator.shell import Shell


def main() -> int:
    """Create the GUI and process events until exit."""
    root = tk.Tk()
    Terminal(root, Shell())
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
