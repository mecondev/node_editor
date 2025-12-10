"""Graphics representation of a Socket."""

from typing import TYPE_CHECKING

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPen
from PyQt5.QtWidgets import QGraphicsItem

from node_editor.themes.theme_engine import ThemeEngine

if TYPE_CHECKING:
    from node_editor.core.socket import Socket


class QDMGraphicsSocket(QGraphicsItem):
    """Class representing graphic Socket in QGraphicsScene.

    Visual representation of a socket with theme support.

    Attributes:
        socket: Reference to logical socket
        isHighlighted: Whether socket is highlighted for connection
        radius: Socket circle radius in pixels
        outline_width: Width of socket outline
    """

    def __init__(self, socket: "Socket"):
        """Initialize graphics socket.

        Args:
            socket: Reference to logical socket
        """
        super().__init__(socket.node.grNode)

        self.socket = socket

        self.isHighlighted = False

        self.radius = 6
        self.outline_width = 1
        self.initAssets()

    @property
    def socket_type(self) -> int:
        """Get socket type from logical socket.

        Returns:
            Socket type identifier
        """
        return self.socket.socket_type

    def getSocketColor(self, key: int | str) -> QColor:
        """Get color for socket type.

        Uses theme engine for socket colors.

        Args:
            key: Socket type (int) or color string

        Returns:
            QColor for this socket type
        """
        theme = ThemeEngine.current_theme
        if isinstance(key, int):
            # Get socket color from theme
            if 0 <= key < len(theme.socket_colors):
                return theme.socket_colors[key]
            return theme.socket_colors[0]  # Default to first color
        elif isinstance(key, str):
            return QColor(key)
        return Qt.GlobalColor.transparent

    def changeSocketType(self) -> None:
        """Change socket type and update colors."""
        self._color_background = self.getSocketColor(self.socket_type)
        self._brush = QBrush(self._color_background)
        self.update()

    def initAssets(self) -> None:
        """Initialize Qt objects like QColor, QPen and QBrush."""
        theme = ThemeEngine.current_theme

        # Socket colors from theme
        self._color_background = self.getSocketColor(self.socket_type)
        self._color_outline = theme.socket_outline_color
        self._color_highlight = theme.socket_highlight_color

        # Pens and brushes
        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._pen_highlight = QPen(self._color_highlight)
        self._pen_highlight.setWidthF(2.0)
        self._brush = QBrush(self._color_background)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None) -> None:
        """Paint socket as a circle.

        Args:
            painter: QPainter to use
            QStyleOptionGraphicsItem: Style options
            widget: Widget being painted on
        """
        painter.setBrush(self._brush)
        painter.setPen(self._pen if not self.isHighlighted else self._pen_highlight)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def boundingRect(self) -> QRectF:
        """Define Qt bounding rectangle for drawing.

        Returns:
            QRectF bounding rectangle
        """
        return QRectF(
            -self.radius - self.outline_width,
            -self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )
