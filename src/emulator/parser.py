"""Command parsing shared by the GUI and startup scripts."""


def parse_command(line: str) -> list[str]:
    """Split input on whitespace, as required by the assignment."""
    return line.split()
