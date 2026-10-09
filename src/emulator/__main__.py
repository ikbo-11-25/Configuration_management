"""Launch the graphical shell emulator."""

import tkinter as tk

from emulator.config import parse_config
from emulator.gui import Terminal
from emulator.shell import Shell
from emulator.startup import run_script


def main(argv: list[str] | None = None) -> int:
    """Run the configured script in the GUI or diagnostic mode."""
    config = parse_config(argv)
    shell = Shell(config)
    if config.headless:
        print(config.dump())
        status = run_script(shell, config.startup, print)
        return int(status.failed)
    root = tk.Tk()
    terminal = Terminal(root, shell)
    terminal.write(config.dump())
    if config.startup:
        root.after(0, lambda: start_in_gui(terminal))
    root.mainloop()
    return 0


def start_in_gui(terminal: Terminal) -> None:
    """Replay startup input and preserve the GUI after script errors."""
    status = run_script(terminal.shell, terminal.shell.config.startup,
                        terminal.write)
    terminal.prompt.configure(text=terminal.shell.prompt)
    if status.exit_requested:
        terminal.root.destroy()


if __name__ == "__main__":
    raise SystemExit(main())
