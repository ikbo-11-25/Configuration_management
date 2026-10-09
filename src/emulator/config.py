"""Command-line configuration and key-value diagnostic output."""

import argparse
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Config:
    """Paths and interface settings selected at application startup."""

    vfs: Path = PROJECT_ROOT / "examples" / "vfs" / "deep"
    startup: Path | None = None
    headless: bool = False

    def dump(self) -> str:
        """Return all settings, one key=value pair per line."""
        startup = str(self.startup) if self.startup else "(none)"
        return "\n".join([
            f"vfs={self.vfs}", f"startup={startup}",
            f"headless={str(self.headless).lower()}",
        ])


def parse_config(argv: list[str] | None = None) -> Config:
    """Parse supported options; physical paths may contain spaces."""
    parser = argparse.ArgumentParser(
        description="GUI UNIX shell emulator, variant 30",
    )
    parser.add_argument("--vfs", type=Path, default=Config().vfs,
                        help="directory to load into memory")
    parser.add_argument("--startup", type=Path,
                        help="UTF-8 startup script, stops on first error")
    parser.add_argument("--headless", action="store_true",
                        help="run a startup script without opening the GUI")
    options = parser.parse_args(argv)
    if options.headless and options.startup is None:
        parser.error("--headless requires --startup")
    startup = options.startup.resolve() if options.startup else None
    return Config(options.vfs.resolve(), startup, options.headless)
