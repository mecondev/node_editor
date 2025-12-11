"""
Graphics representation of an Edge.

Author: Michael Economou
Date: 2025-12-11
"""

from typing import TYPE_CHECKING

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QPainterPath, QPen
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPathItem, QWidget

from node_editor.graphics.edge_path import (
    GraphicsEdgePathBezier,
    GraphicsEdgePathDirect,
    GraphicsEdgePathImprovedBezier,
    GraphicsEdgePathImprovedSharp,
    GraphicsEdgePathSquare,
)
from node_editor.themes.theme_engine import ThemeEngine

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QGraphicsSceneHoverEvent, QStyleOptionGraphicsItem

    from node_editor.core.edge import Edge


class QDMGraphicsEdge(QGraphicsPathItem):
    """Base class for graphics edge.

    Handles visual representation of edges with different path styles.

    Attributes:
        edge: Reference to logical Edge
        pathCalculator: Instance calculating the path to draw
        posSource: [x, y] source position in scene
        posDestination: [x, y] destination position in scene
        hovered: Whether mouse is hovering over edge
    """

    def __init__(self, edge: "Edge", parent: QWidget | None = None):
        """Initialize graphics edge.

        Args:
            edge: Reference to logical Edge
            parent: Parent widget
        """
        super().__init__(parent)

        self.edge = edge

        # Create instance of path calculator
        self.pathCalculator = self.determineEdgePathClass()(self)

        # Interaction flags
        self._last_selected_state = False
        self.hovered = False

        # Position variables
        self.posSource = [0, 0]
        self.posDestination = [200, 100]

        self.initAssets()
        self.initUI()

    def initUI(self) -> None:
        """Set up QGraphicsPathItem."""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)

    def initAssets(self) -> None:
        """Initialize Qt objects like QColor, QPen using theme."""
        theme = ThemeEngine.current_theme()

        # Edge colors from theme
        self._color = self._default_color = theme.edge_color
        self._color_selected = theme.edge_selected_color
        self._color_hovered = theme.edge_hovered_color

        # Pens for different states
        self._pen = QPen(self._color)
        self._pen_selected = QPen(self._color_selected)
        self._pen_dragging = QPen(self._color)
        self._pen_hovered = QPen(self._color_hovered)

        self._pen_dragging.setStyle(Qt.PenStyle.DashLine)
        self._pen.setWidthF(theme.edge_width)
        self._pen_selected.setWidthF(theme.edge_width)
        self._pen_dragging.setWidthF(theme.edge_width)
        self._pen_hovered.setWidthF(theme.edge_width + 2.0)

    def createEdgePathCalculator(self):
        """Create instance of GraphicsEdgePathBase.

        Returns:
            Path calculator instance
        """
        self.pathCalculator = self.determineEdgePathClass()(self)
        return self.pathCalculator

    def determineEdgePathClass(self):
        """Determine which path class to use based on edge_type.

        Returns:
            GraphicsEdgePath class
        """
        from node_editor.core.edge import (
            EDGE_TYPE_BEZIER,
            EDGE_TYPE_DIRECT,
            EDGE_TYPE_IMPROVED_BEZIER,
            EDGE_TYPE_IMPROVED_SHARP,
            EDGE_TYPE_SQUARE,
        )

        if self.edge.edge_type == EDGE_TYPE_BEZIER:
            return GraphicsEdgePathBezier
        if self.edge.edge_type == EDGE_TYPE_DIRECT:
            return GraphicsEdgePathDirect
        if self.edge.edge_type == EDGE_TYPE_SQUARE:
            return GraphicsEdgePathSquare
        if self.edge.edge_type == EDGE_TYPE_IMPROVED_SHARP:
            return GraphicsEdgePathImprovedSharp
        if self.edge.edge_type == EDGE_TYPE_IMPROVED_BEZIER:
            return GraphicsEdgePathImprovedBezier

        return GraphicsEdgePathImprovedBezier

    def makeUnselectable(self) -> None:
        """Disable click detection (used for drag edges)."""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setAcceptHoverEvents(False)

    def changeColor(self, color) -> None:
        """Change color of the edge.

        Args:
            color: Color as string hex '#00ff00' or QColor
        """
        from PyQt5.QtGui import QColor

        self._color = QColor(color) if isinstance(color, str) else color
        self._pen = QPen(self._color)
        self._pen.setWidthF(ThemeEngine.current_theme().edge_width)

    def setColorFromSockets(self) -> bool:
        """Change color according to connected sockets.

        Returns:
            True if color was determined
        """
        socket_type_start = self.edge.start_socket.socket_type
        socket_type_end = self.edge.end_socket.socket_type
        if socket_type_start != socket_type_end:
            return False
        self.changeColor(self.edge.start_socket.grSocket.getSocketColor(socket_type_start))
        return True

    def onSelected(self) -> None:
        """Event handler when edge was selected."""
        self.edge.scene.grScene.item_selected.emit()

    def doSelect(self, new_state: bool = True) -> None:
        """Safe version of selecting the graphics edge.

        Args:
            new_state: True to select, False to deselect
        """
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state:
            self.onSelected()

    def mouseReleaseEvent(self, event) -> None:
        """Handle selecting and deselecting edge.

        Args:
            event: Qt mouse event
        """
        super().mouseReleaseEvent(event)
        if self._last_selected_state != self.isSelected():
            self.edge.scene.resetLastSelectedStates()
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def hoverEnterEvent(self, _event: "QGraphicsSceneHoverEvent") -> None:
        """Handle hover enter.

        Args:
            event: Qt hover event
        """
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, _event: "QGraphicsSceneHoverEvent") -> None:
        """Handle hover leave.

        Args:
            event: Qt hover event
        """
        self.hovered = False
        self.update()

    def setSource(self, x: float, y: float) -> None:
        """Set source point.

        Args:
            x: X position
            y: Y position
        """
        self.posSource = [x, y]

    def setDestination(self, x: float, y: float) -> None:
        """Set destination point.

        Args:
            x: X position
            y: Y position
        """
        self.posDestination = [x, y]

    def boundingRect(self) -> QRectF:
        """Define Qt bounding rectangle.

        Returns:
            QRectF bounding rectangle
        """
        return self.shape().boundingRect()

    def shape(self) -> QPainterPath:
        """Get QPainterPath representation of edge.

        Returns:
            Path representation
        """
        return self.calcPath()

    def paint(
        self,
        painter,
        _option: "QStyleOptionGraphicsItem",
        _widget=None,
    ) -> None:
        """Paint the graphics edge.

        Args:
            painter: QPainter to use
            QStyleOptionGraphicsItem: Style options
            widget: Widget being painted on
        """
        self.setPath(self.calcPath())

        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Draw hover highlight
        if self.hovered and self.edge.end_socket is not None:
            painter.setPen(self._pen_hovered)
            painter.drawPath(self.path())

        # Draw edge
        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)

        painter.drawPath(self.path())

    def intersectsWith(self, p1: QPointF, p2: QPointF) -> bool:
        """Check if edge intersects with line between two points.

        Args:
            p1: Point A
            p2: Point B

        Returns:
            True if edge intersects with line
        """
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calcPath()
        return cutpath.intersects(path)

    def calcPath(self) -> QPainterPath:
        """Calculate QPainterPath from source to destination.

        Uses pathCalculator instance to compute the path.

        Returns:
            QPainterPath connecting source and destination
        """
        return self.pathCalculator.calcPath()
