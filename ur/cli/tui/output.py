import os
import sys

from ur.cli.tui.constants import ANSI_ESCAPE, C_BOARD, C_BOLD_TEXT, C_RESET


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


def center_in(text: str, width: int, fill: str = " ") -> str:
    """Return `text` padded symmetrically to fill `width` visible chars.

    Unlike ``center()``, which only adds left padding to align in the
    terminal, this pads both sides — intended for centering content inside
    a fixed-width box column. ``fill`` controls the padding character.
    """
    pad_total = max(0, width - ansi_len(text))
    pad_l = pad_total // 2
    pad_r = pad_total - pad_l
    return fill * pad_l + text + fill * pad_r


def out(text: str, end: str = "\n") -> None:
    """Write `text` to stdout with `end` appended, then flush."""
    sys.stdout.write(text + end)
    sys.stdout.flush()


def ansi_len(s: str) -> int:
    """Visible length of a string after stripping ANSI escape codes."""
    return len(ANSI_ESCAPE.sub('', s))


def ansi_wordwrap(text: str, width: int) -> list[str]:
    """Word-wrap `text` to fit `width` visible chars per line, preserving ANSI codes.

    Explicit ``\\n`` characters are treated as hard line breaks. Each
    paragraph is then greedily filled word by word using visible length.
    Returns a flat list of lines (empty string represents a blank line).
    """
    result = []
    for para in text.split('\n'):
        if not para:
            result.append('')
            continue
        words = para.split(' ')
        cur, cur_len = '', 0
        for word in words:
            wl = ansi_len(word)
            if cur_len == 0:
                cur, cur_len = word, wl
            elif cur_len + 1 + wl <= width:
                cur += ' ' + word
                cur_len += 1 + wl
            else:
                result.append(cur)
                cur, cur_len = word, wl
        result.append(cur)
    return result


def word_wrap(text: str, wrap: int = 100, centered: bool = False) -> str:
    """Return `text` word-wrapped at `wrap` visible chars, preserving ANSI codes.

    With ``centered=True`` each output line is individually centered in the
    terminal. Multiple wrapped lines are joined with ``\\n``.
    """
    lines = ansi_wordwrap(text, wrap)
    if centered:
        return '\n'.join(center(line) for line in lines)
    return '\n'.join(lines)


def print_box(
    text: str,
    title: str = None,
    inner_width: int = 54,
    content_color: str = "",
    title_color: str = None,
) -> None:
    """Print a centered bordered box, optionally with a bold title header.

    Args:
        text: Body text. Hard ``\\n`` breaks are respected; lines that still
              exceed ``inner_width - 2`` are word-wrapped.
        title: Optional header line shown between ``╔╗`` and ``╠╣``.
        inner_width: Visible width between the left and right border chars.
        content_color: ANSI code applied to each body line (e.g. ``C_TUTORIAL``).
        title_color: ANSI code for the title. Defaults to ``C_BOLD_TEXT``.
    """
    if title_color is None:
        title_color = C_BOLD_TEXT

    content_w = inner_width - 2  # 1-space padding on each side

    top = f"{C_BOARD}╔{'═' * inner_width}╗{C_RESET}"
    bot = f"{C_BOARD}╚{'═' * inner_width}╝{C_RESET}"
    sep = f"{C_BOARD}╠{'═' * inner_width}╣{C_RESET}"

    out(f"\n{center(top)}")

    if title:
        out(center(f"{C_BOARD}║{center_in(f'{title_color}{title}{C_RESET}', inner_width)}{C_BOARD}║{C_RESET}"))
        out(center(sep))

    for line in ansi_wordwrap(text, content_w):
        if not line:
            out(center(f"{C_BOARD}║{' ' * inner_width}║{C_RESET}"))
        else:
            pad_r = content_w - ansi_len(line)
            out(center(
                f"{C_BOARD}║{content_color} {line}{C_RESET}{content_color}"
                f"{' ' * pad_r} {C_BOARD}║{C_RESET}"
            ))

    out(center(bot))
