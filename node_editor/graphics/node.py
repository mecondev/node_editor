"""Graphics representation of nodes in the scene.

This module defines QDMGraphicsNode, the Qt graphics item that renders
individual nodes. It handles visual appearance including title bar,
content area, selection states, and hover effects.

The graphics node:
    - Draws rounded rectangle with title and content areas
    - Responds to mouse events for selection and movement
    - Updates connected edges when moved
    - Supports hover highlighting
    - Integrates with theme system for colors

Author:
    Michael Economou

Date:
    2025-12-11
"""

from typing import TYPE_CHECKING

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPainterPath, QPen
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QWidget

from node_editor.themes.theme_engine import ThemeEngine

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QGraphicsSceneHoverEvent, QStyleOptionGraphicsItem

    from node_editor.core.node import Node


class QDMGraphicsNode(QGraphicsItem):
    """Qt graphics item rendering a node in the scene.

    Manages the visual representation of a node including its title bar,
    content widget area, selection highlighting, and hover effects.
    Handles mouse interactions for selection, movement, and double-click.

    Attributes:
        node: Reference to the logical Node model.
        hovered: True while mouse is over this item.
        width: Node width in pixels.
        height: Node height in pixels.
        title_item: QGraphicsTextItem displaying the title.
        grContent: QGraphicsProxyWidget containing content widget.
    """

    def __init__(self, node: "Node", parent: QWidget | None = None):
        """Initialize graphics node for a logical node.

        Args:
            node: Logical Node this graphics item represents.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.node = node

        self.hovered = False
        self._was_moved = False
        self._last_selected_state = False

        self.initSizes()
        self.initAssets()
        self.initUI()

    @property
    def content(self):
        """Content widget of the associated node.

        Returns:
            QDMNodeContentWidget instance or None.
        """
        return self.node.content if self.node else None

    @property
    def title(self) -> str:
        """Display title of this node.

        Returns:
            Current title string.
        """
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """Update displayed title text.

        Args:
            value: New title string.
        """
        self._title = value
        self.title_item.setPlainText(self._title)

    def initUI(self) -> None:
        """Configure item flags and initialize visual components."""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setAcceptHoverEvents(True)

        self.initTitle()
        self.title = self.node.title

        self.initContent()

    def initSizes(self) -> None:
        """Set default dimensions and padding values."""
        self.width = 180
        self.height = 240
        self.edge_roundness = 10.0
        self.edge_padding = 10
        self.title_height = 24
        self.title_horizontal_padding = 4.0
        self.title_vertical_padding = 4.0

    def initAssets(self) -> None:
        """Initialize pens, brushes, and fonts from theme."""
        theme = ThemeEngine.current_theme()

        self._title_color = theme.node_title_color
        self._title_font = QFont(theme.node_title_font)
        self._title_font.setPointSize(theme.node_title_font_size)

        self._color = theme.node_border_default
        self._color_selected = theme.node_border_selected
        self._color_hovered = theme.node_border_hovered

        self._pen_default = QPen(self._color)
        self._pen_default.setWidthF(theme.node_border_width)
        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(theme.node_border_width)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_hovered.setWidthF(theme.node_border_width_hovered)
        
        # Error state pen - red color for invalid nodes
        self._pen_error = QPen(QColor("#FF5555"))
        self._pen_error.setWidthF(2.5)

        self._brush_title = QBrush(theme.node_title_background)
        self._brush_background = QBrush(theme.node_background)

    def onSelected(self) -> None:
        """Emit selection signal to scene.

        Called when node becomes selected to notify listeners.
        """
        self.node.scene.grScene.item_selected.emit()

    def doSelect(self, new_state: bool = True) -> None:
        """Programmatically select or deselect this node.

        Updates internal state tracking and emits signal if selecting.

        Args:
            new_state: True to select, False to deselect.
        """
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state:
            self.onSelected()

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse drag to move node and update edges.

        Args:
            event: Qt mouse move event.
        """
        super().mouseMoveEvent(event)

        for node in self.scene().scene.nodes:
            if node.grNode.isSelected():
                node.updateConnectedEdges()
        self._was_moved = True

    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release to store history and update selection.

        Args:
            event: Qt mouse release event.
        """
        super().mouseReleaseEvent(event)

        if self._was_moved:
            self._was_moved = False
            self.node.scene.history.storeHistory("Node moved", set_modified=True)

            self.node.scene.resetLastSelectedStates()
            self.doSelect()

            self.node.scene._last_selected_items = self.node.scene.getSelectedItems()
            return

        if (
            self._last_selected_state != self.isSelected()
            or self.node.scene._last_selected_items != self.node.scene.getSelectedItems()
        ):
            self.node.scene.resetLastSelectedStates()
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def mouseDoubleClickEvent(self, event) -> None:
        """Forward double-click to logical node handler.

        Args:
            event: Qt mouse double-click event.
        """
        self.node.onDoubleClicked(event)

    def hoverEnterEvent(self, _event: "QGraphicsSceneHoverEvent") -> None:
        """Enable hover highlighting when mouse enters.

        Args:
            _event: Qt hover enter event (unused).
        """
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, _event: "QGraphicsSceneHoverEvent") -> None:
        """Disable hover highlighting when mouse leaves.

        Args:
            _event: Qt hover leave event (unused).
        """
        self.hovered = False
        self.update()

    def boundingRect(self) -> QRectF:
        """Return bounding rectangle for Qt graphics framework.

        Returns:
            QRectF defining item bounds.
        """
        return QRectF(0, 0, self.width, self.height).normalized()

    def initTitle(self) -> None:
        """Create and configure title text item."""
        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = self.node  # type: ignore
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self.title_horizontal_padding, 0)
        self.title_item.setTextWidth(self.width - 2 * self.title_horizontal_padding)

    def initContent(self) -> None:
        """Embed content widget as graphics proxy within node."""
        if self.content is not None:
            self.content.setGeometry(
                self.edge_padding,
                self.title_height + self.edge_padding,
                self.width - 2 * self.edge_padding,
                self.height - 2 * self.edge_padding - self.title_height,
            )

        self.grContent = self.node.scene.grScene.addWidget(self.content)
        self.grContent.node = self.node  # type: ignore
        self.grContent.setParentItem(self)

    def paint(self, painter, _option: "QStyleOptionGraphicsItem", _widget=None) -> None:
        """Render node with title bar, content area, and outline.

        Draws rounded rectangles for title and content backgrounds,
        then draws border with appropriate color for selection/hover state.

        Args:
            painter: QPainter for drawing operations.
            _option: Style options (unused).
            _widget: Target widget (unused).
        """
        path_title = QPainterPath()
        path_title.setFillRule(Qt.FillRule.WindingFill)
        path_title.addRoundedRect(
            0, 0, self.width, self.title_height, self.edge_roundness, self.edge_roundness
        )
        path_title.addRect(
            0, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness
        )
        path_title.addRect(
            self.width - self.edge_roundness,
            self.title_height - self.edge_roundness,
            self.edge_roundness,
            self.edge_roundness,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        path_content = QPainterPath()
        path_content.setFillRule(Qt.FillRule.WindingFill)
        path_content.addRoundedRect(
            0,
            self.title_height,
            self.width,
            self.height - self.title_height,
            self.edge_roundness,
            self.edge_roundness,
        )
        path_content.addRect(0, self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(
            self.width - self.edge_roundness,
            self.title_height,
            self.edge_roundness,
            self.edge_roundness,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        path_outline = QPainterPath()
        path_outline.addRoundedRect(
            -1, -1, self.width + 2, self.height + 2, self.edge_roundness, self.edge_roundness
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Check if node is in error state
        if self.node and self.node.isInvalid():
            painter.setPen(self._pen_error)
            painter.drawPath(path_outline.simplified())
        elif self.hovered:
            painter.setPen(self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
            painter.drawPath(path_outline.simplified())
