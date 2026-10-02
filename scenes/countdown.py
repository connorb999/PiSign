# =============================================================================
# scenes/countdown.py — Full-panel countdown to a target datetime
# =============================================================================

import datetime
from rgbmatrix import RGBMatrix

import config
from scenes.base_scene import BaseScene
from utils.colors import WHITE, DIM_WHITE, YELLOW, CYAN, RED, DARK_GRAY
from utils.fonts import load_font


class CountdownScene(BaseScene):
    """
    Fills the entire panel with a large countdown to a target datetime.

    Layout (64×64 example):
      ┌──────────────────────────────┐
      │        NEW YEAR'S EVE        │  ← label (target date)
      │                              │
      │     12d  04h  33m  07s       │  ← large digits
      │      DD   HH   MM   SS       │  ← unit labels
      │                              │
      │    Fri Dec 31  11:59 PM      │  ← target date/time
      └──────────────────────────────┘

    When the countdown reaches zero it displays "NOW!" and stops counting.
    """

    def __init__(self, matrix: RGBMatrix, target: datetime.datetime):
        super().__init__(matrix)
        # Ensure target is timezone-aware (assume local time if naive)
        if target.tzinfo is None:
            target = target.astimezone()
        self._target = target
        self._font_large  = load_font(config.FONT_LARGE)
        self._font_medium = load_font(config.FONT_MEDIUM)
        self._font_small  = load_font(config.FONT_SMALL)

    # ------------------------------------------------------------------
    def render(self) -> None:
        self._clear_region(0, self.matrix.height)
        w = self.matrix.width

        now    = datetime.datetime.now().astimezone()
        delta  = self._target - now
        total  = int(delta.total_seconds())

        if total <= 0:
            self._render_zero()
            return

        days    = total // 86400
        hours   = (total % 86400) // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60

        # --- Row 0–8: target label (event name derived from date) ---
        label = self._target.strftime("%b %-d, %Y").upper()
        lx = max(1, (w - len(label) * 6) // 2)
        self._draw_text(self._font_small, lx, 8, CYAN, label)

        # Separator
        self._draw_line(0, 10, w - 1, 10, DARK_GRAY)

        # --- Row 12–30: large countdown numbers ---
        # Build segments: only show days if > 0
        if days > 0:
            segments = [
                (f"{days:02d}", "D"),
                (f"{hours:02d}", "H"),
                (f"{minutes:02d}", "M"),
                (f"{seconds:02d}", "S"),
            ]
        else:
            segments = [
                (f"{hours:02d}", "H"),
                (f"{minutes:02d}", "M"),
                (f"{seconds:02d}", "S"),
            ]

        n = len(segments)
        # Each segment is ~14px wide (9px font + 5px gap), centered
        seg_w   = 14
        total_w = n * seg_w - 2
        start_x = max(1, (w - total_w) // 2)

        for i, (value, unit) in enumerate(segments):
            x = start_x + i * seg_w

            # Pulse seconds digit — dim on even seconds for a tick effect
            if unit == "S" and (int(total) % 2 == 0):
                num_color = YELLOW
            elif unit == "S":
                num_color = (180, 140, 0)
            elif unit == "D":
                num_color = RED
            else:
                num_color = WHITE

            self._draw_text(self._font_large,  x, 28, num_color, value)
            self._draw_text(self._font_small,  x + 2, 36, DIM_WHITE, unit)

            # Colon separator between segments
            if i < n - 1:
                cx = x + seg_w - 3
                self._set_pixel(cx, 22, DARK_GRAY)
                self._set_pixel(cx, 26, DARK_GRAY)

        # Separator
        self._draw_line(0, 40, w - 1, 40, DARK_GRAY)

        # --- Row 42–50: target date and time ---
        target_str  = self._target.strftime("%a %b %-d")
        target_time = self._target.strftime("%-I:%M %p")
        tx = max(1, (w - len(target_str) * 6) // 2)
        tt = max(1, (w - len(target_time) * 6) // 2)
        self._draw_text(self._font_small, tx, 49, DIM_WHITE, target_str)
        self._draw_text(self._font_small, tt, 57, DIM_WHITE, target_time)

    # ------------------------------------------------------------------
    def _render_zero(self):
        """Display a 'NOW!' celebration when countdown reaches zero."""
        w = self.matrix.width
        h = self.matrix.height

        # Alternate colors each second for a celebratory flash
        tick   = int(datetime.datetime.now().timestamp()) % 2
        color  = YELLOW if tick == 0 else CYAN

        msg  = "NOW!"
        msg2 = self._target.strftime("%b %-d").upper()

        mx  = max(1, (w - len(msg)  * 9) // 2)
        mx2 = max(1, (w - len(msg2) * 6) // 2)

        self._draw_text(self._font_large,  mx,  h // 2,     color,    msg)
        self._draw_text(self._font_small,  mx2, h // 2 + 12, DIM_WHITE, msg2)
