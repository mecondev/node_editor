"""Graphics representation of Scene."""

import math
from typing import TYPE_CHECKING

from PyQt5.QtCore import QLine, QRect, Qt, pyqtSignal as Signal
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsScene, QWidget

from node_editor.themes.theme_engine import ThemeEngine

if TYPE_CHECKING:
    from node_editor.core.scene import Scene

# Import DEBUG_STATE from view (will be set later)
DEBUG_STATE = False


class QDMGraphicsScene(QGraphicsScene):
    """Graphics representation of Scene.

    Handles grid background drawing and item selection events.

    Attributes:
        scene: Reference to logical Scene
        gridSize: Size of grid cells in pixels
        gridSquares: Number of grid cells between dark lines
    """

    # Signals
    item_selected = Signal()
    items_deselected = Signal()

    def __init__(self, scene: "Scene", parent: QWidget | None = None):
        """Initialize graphics scene.

        Args:
            scene: Reference to logical Scene
            parent: Parent widget
        """
        super().__init__(parent)

        self.scene = scene

        # Fix Qt bug with item removal
        # https://bugreports.qt.io/browse/QTBUG-18021
        # https://bugreports.qt.io/browse/QTBUG-50691
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)

        # Grid settings
        self.gridSize = 20
        self.gridSquares = 5

        self.initAssets()
        self.setBackgroundBrush(self._color_background)

    def initAssets(self) -> None:
        """Initialize Qt objects using theme."""
        theme = ThemeEngine.current_theme

        # Scene colors from theme
        self._color_background = theme.scene_background
        self._color_light = theme.scene_grid_light
        self._color_dark = theme.scene_grid_dark
        self._color_state = QColor("#cccccc")

        # Grid pens
        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        # State display pen and font
        self._pen_state = QPen(self._color_state)
        self._font_state = QFont("Ubuntu", 16)

    def dragMoveEvent(self, event) -> None:
        """Enable Qt drag events.

        Args:
            event: Qt drag event
        """

    def setGrScene(self, width: int, height: int) -> None:
        """Set width and height of graphics scene.

        Args:
            width: Scene width in pixels
            height: Scene height in pixels
        """
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter: QPainter, rect: QRect) -> None:
        """Draw background grid.

        Args:
            painter: QPainter to use
            rect: Rectangle area to draw
        """
        super().drawBackground(painter, rect)

        # Create grid
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.gridSize)
        first_top = top - (top % self.gridSize)

        # Compute all lines to be drawn
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.gridSize):
            if (x % (self.gridSize * self.gridSquares) != 0):
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.gridSize):
            if (y % (self.gridSize * self.gridSquares) != 0):
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))

        # Draw the lines
        painter.setPen(self._pen_light)
        try:
            painter.drawLines(*lines_light)  # PyQt5
        except TypeError:
            painter.drawLines(lines_light)  # PySide2

        painter.setPen(self._pen_dark)
        try:
            painter.drawLines(*lines_dark)  # PyQt5
        except TypeError:
            painter.drawLines(lines_dark)  # PySide2

        # Draw state debug info if enabled
        if DEBUG_STATE:
            try:
                from node_editor.graphics.view import STATE_STRING

                painter.setFont(self._font_state)
                painter.setPen(self._pen_state)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
                offset = 14
                rect_state = QRect(
                    rect.x() + offset,
                    rect.y() + offset,
                    rect.width() - 2 * offset,
                    rect.height() - 2 * offset,
                )
                painter.drawText(
                    rect_state,
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
                    STATE_STRING[self.views()[0].mode].upper(),
                )
            except Exception:
                pass
