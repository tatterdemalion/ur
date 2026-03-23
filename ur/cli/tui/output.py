import os
import sys
import textwrap

from ur.cli.tui.constants import ANSI_ESCAPE


def _terminal_width() -> int:
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80


def center(text: str, offset: int=0) -> str:
    """Return `text` prefixed with spaces to center it in the terminal.

    Strips ANSI codes when measuring visible width, and preserves any
    leading newlines so they appear before the padding.
    """
    cols = _terminal_width()
    stripped = text.lstrip("\n")
    leading = "\n" * (len(text) - len(stripped))
    visible = ANSI_ESCAPE.sub("", stripped)
    pad = " " * max(0, (cols - len(visible)) // 2)
    return leading + (" " * offset) + pad + stripped


def out(text: str, end: str = "\n") -> None:
    """Write `text` to stdout with `end` appended, then flush."""
    sys.stdout.write(text + end)
    sys.stdout.flush()


def word_wrap(text: str, wrap: int = 120, centered: bool = False) -> str:
    """Print text centered in the terminal, word-wrapping at `wrap` visible chars."""
    plain = ANSI_ESCAPE.sub("", text)
    if len(plain) <= wrap:
        return center(text) if centered else text
    else:
        for line in textwrap.wrap(plain, wrap):
            return center(line) if centered else line
