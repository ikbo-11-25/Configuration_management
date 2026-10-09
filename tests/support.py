"""Portable temporary directories confined to this test project."""

import shutil
from contextlib import contextmanager
from uuid import uuid4

from emulator.config import PROJECT_ROOT


@contextmanager
def temporary_directory():
    """Create an isolated test folder, then safely remove that folder."""
    base = (PROJECT_ROOT / ".test-work").resolve()
    base.mkdir(exist_ok=True)
    target = base / uuid4().hex
    target.mkdir()
    try:
        yield str(target)
    finally:
        if target.resolve().parent != base:
            raise RuntimeError("test cleanup escaped its workspace")
        shutil.rmtree(target)
