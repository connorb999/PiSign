# =============================================================================
# utils/fonts.py — Font loading helpers for rpi-rgb-led-matrix
# =============================================================================

import os
from rgbmatrix import graphics


_font_cache: dict = {}


def load_font(path: str) -> graphics.Font:
    """Load a BDF font, caching by path to avoid repeated disk reads."""
    if path not in _font_cache:
        font = graphics.Font()
        abs_path = os.path.join(os.path.dirname(__file__), "..", path)
        abs_path = os.path.abspath(abs_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(
                f"Font not found: {abs_path}\n"
                "Run install_fonts.sh to download BDF fonts."
            )
        font.LoadFont(abs_path)
        _font_cache[path] = font
    return _font_cache[path]


def text_width(font: graphics.Font, text: str) -> int:
    """Approximate pixel width of a string in the given font."""
    # BDF fonts report character width via the font object
    # This is an approximation; exact width depends on the font metrics
    return sum(font.CharacterWidth(ord(c)) for c in text)
