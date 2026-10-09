"""Tkinter graphical terminal with a separate command input field."""

import getpass
import socket
import tkinter as tk
from tkinter import scrolledtext

from emulator.shell import Shell


class Terminal:
    """Display shell input and output in a graphical window."""

    def __init__(self, root: tk.Tk, shell: Shell) -> None:
        """Build a terminal using the real host username and hostname."""
        self.root = root
        self.shell = shell
        identity = f"{getpass.getuser()}@{socket.gethostname()}"
        root.title(f"Эмулятор - [{identity}]")
        root.geometry("920x600")
        self.output = scrolledtext.ScrolledText(
            root, bg="#101820", fg="#dce7ef", insertbackground="white",
            font=("Consolas", 11), state="disabled", wrap="none",
        )
        self.output.pack(fill="both", expand=True, padx=12, pady=12)
        controls = tk.Frame(root)
        controls.pack(fill="x", padx=12, pady=(0, 12))
        self.prompt = tk.Label(controls, text=shell.prompt)
        self.prompt.pack(side="left")
        self.entry = tk.Entry(controls, font=("Consolas", 11))
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.submit)
        tk.Button(controls, text="Выполнить", command=self.submit).pack(
            side="right", padx=(8, 0),
        )
        self.write("Вариант 30. Для завершения введите exit.")
        self.entry.focus_set()

    def write(self, text: str) -> None:
        """Append text to the read-only terminal output."""
        if not text:
            return
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.configure(state="disabled")
        self.output.see("end")

    def submit(self, event: object = None) -> None:
        """Execute one interactive command and update the prompt."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.write(self.shell.prompt + line)
        result = self.shell.execute(line)
        self.write(result.output)
        self.prompt.configure(text=self.shell.prompt)
        if result.exit_requested:
            self.root.destroy()
