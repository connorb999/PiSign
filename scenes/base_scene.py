# =============================================================================
# scenes/base_scene.py — Abstract base class for all display scenes
# =============================================================================

from abc import ABC, abstractmethod
from rgbmatrix import RGBMatrix, graphics


class BaseScene(ABC):
    """
    All scenes inherit from this class.

    Each scene receives the shared matrix canvas and is responsible for
    drawing its portion of the screen during render().

    Scenes should be stateless in terms of layout — recalculate positions
    each render() call based on current data.
    """

    def __init__(self, matrix: RGBMatrix):
        self.matrix = matrix
        self.canvas = matrix.CreateFrameCanvas()

    @abstractmethod
    def render(self) -> None:
        """Draw content onto self.canvas, then call self._swap()."""
        ...

    def _swap(self) -> None:
        """Push canvas to display (double-buffer swap)."""
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def _clear_region(self, top: int, bottom: int) -> None:
        """Clear a horizontal band of the canvas."""
        for y in range(top, bottom):
            for x in range(self.matrix.width):
                self.canvas.SetPixel(x, y, 0, 0, 0)

    def _draw_text(
        self,
        font: graphics.Font,
        x: int,
        y: int,
        color: tuple,
        text: str,
    ) -> int:
        """
        Draw text and return the pixel width consumed.
        color is an (R, G, B) tuple.
        """
        c = graphics.Color(*color)
        return graphics.DrawText(self.canvas, font, x, y, c, text)

    def _draw_line(
        self,
        x0: int, y0: int,
        x1: int, y1: int,
        color: tuple,
    ) -> None:
        c = graphics.Color(*color)
        graphics.DrawLine(self.canvas, x0, y0, x1, y1, c)

    def _set_pixel(self, x: int, y: int, color: tuple) -> None:
        self.canvas.SetPixel(x, y, *color)
