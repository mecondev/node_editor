"""Graphics representation of a Node."""

from typing import TYPE_CHECKING

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPainterPath, QPen
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QWidget

from node_editor.themes.theme_engine import ThemeEngine

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QGraphicsSceneHoverEvent, QStyleOptionGraphicsItem

    from node_editor.core.node import Node


class QDMGraphicsNode(QGraphicsItem):
    """Class describing graphics representation of Node.

    Handles visual appearance, selection, hover effects, and mouse interaction.

    Attributes:
        node: Reference to logical Node
        hovered: Whether mouse is hovering over node
        width: Node width in pixels
        height: Node height in pixels
        title_item: QGraphicsTextItem for title text
        grContent: QGraphicsProxyWidget for content widget
    """

    def __init__(self, node: "Node", parent: QWidget | None = None):
        """Initialize graphics node.

        Args:
            node: Reference to logical Node
            parent: Parent widget
        """
        super().__init__(parent)
        self.node = node

        # Interaction flags
        self.hovered = False
        self._was_moved = False
        self._last_selected_state = False

        self.initSizes()
        self.initAssets()
        self.initUI()

    @property
    def content(self):
        """Reference to node content widget.

        Returns:
            QDMNodeContentWidget or None
        """
        return self.node.content if self.node else None

    @property
    def title(self) -> str:
        """Title of this node.

        Returns:
            Current node title
        """
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """Set node title.

        Args:
            value: New title text
        """
        self._title = value
        self.title_item.setPlainText(self._title)

    def initUI(self) -> None:
        """Set up QGraphicsItem flags and content."""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setAcceptHoverEvents(True)

        # Initialize title
        self.initTitle()
        self.title = self.node.title

        self.initContent()

    def initSizes(self) -> None:
        """Set up internal size attributes."""
        self.width = 180
        self.height = 240
        self.edge_roundness = 10.0
        self.edge_padding = 10
        self.title_height = 24
        self.title_horizontal_padding = 4.0
        self.title_vertical_padding = 4.0

    def initAssets(self) -> None:
        """Initialize Qt objects like QColor, QPen and QBrush using theme."""
        theme = ThemeEngine.current_theme

        # Title styling
        self._title_color = theme.node_title_color
        self._title_font = QFont(theme.node_title_font, theme.node_title_font_size)

        # Node colors from theme
        self._color = theme.node_outline_color
        self._color_selected = theme.node_selected_color
        self._color_hovered = QColor("#FF37A6FF")  # Keep this bright blue for hover

        # Pens for outlines
        self._pen_default = QPen(self._color)
        self._pen_default.setWidthF(2.0)
        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(2.0)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_hovered.setWidthF(3.0)

        # Brushes for backgrounds
        self._brush_title = QBrush(theme.node_title_background)
        self._brush_background = QBrush(theme.node_background)

    def onSelected(self) -> None:
        """Event handler when node is selected."""
        self.node.scene.grScene.itemSelected.emit()

    def doSelect(self, new_state: bool = True) -> None:
        """Safe version of selecting the graphics node.

        Takes care of selection state flag used internally.

        Args:
            new_state: True to select, False to deselect
        """
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state:
            self.onSelected()

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move - update connected edges.

        Args:
            event: Qt mouse event
        """
        super().mouseMoveEvent(event)

        # Update connected edges for all selected nodes
        for node in self.scene().scene.nodes:
            if node.grNode.isSelected():
                node.updateConnectedEdges()
        self._was_moved = True

    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release - store history and selection.

        Args:
            event: Qt mouse event
        """
        super().mouseReleaseEvent(event)

        # Handle node movement
        if self._was_moved:
            self._was_moved = False
            self.node.scene.history.storeHistory("Node moved", setModified=True)

            self.node.scene.resetLastSelectedStates()
            self.doSelect()  # Trigger itemSelected when node moved

            # Store last selected state
            self.node.scene._last_selected_items = self.node.scene.getSelectedItems()
            return

        # Handle selection change
        if (
            self._last_selected_state != self.isSelected()
            or self.node.scene._last_selected_items != self.node.scene.getSelectedItems()
        ):
            self.node.scene.resetLastSelectedStates()
            self._last_selected_state = self.isSelected()
            self.onSelected()

    def mouseDoubleClickEvent(self, event) -> None:
        """Handle double click event.

        Args:
            event: Qt mouse event
        """
        self.node.onDoubleClicked(event)

    def hoverEnterEvent(self, event: "QGraphicsSceneHoverEvent") -> None:
        """Handle hover enter.

        Args:
            event: Qt hover event
        """
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event: "QGraphicsSceneHoverEvent") -> None:
        """Handle hover leave.

        Args:
            event: Qt hover event
        """
        self.hovered = False
        self.update()

    def boundingRect(self) -> QRectF:
        """Define Qt bounding rectangle.

        Returns:
            QRectF bounding rectangle
        """
        return QRectF(0, 0, self.width, self.height).normalized()

    def initTitle(self) -> None:
        """Set up title graphics representation."""
        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = self.node  # type: ignore
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self.title_horizontal_padding, 0)
        self.title_item.setTextWidth(self.width - 2 * self.title_horizontal_padding)

    def initContent(self) -> None:
        """Set up grContent QGraphicsProxyWidget for content widget."""
        if self.content is not None:
            self.content.setGeometry(
                self.edge_padding,
                self.title_height + self.edge_padding,
                self.width - 2 * self.edge_padding,
                self.height - 2 * self.edge_padding - self.title_height,
            )

        # Add widget to scene as QGraphicsProxyWidget
        self.grContent = self.node.scene.grScene.addWidget(self.content)
        self.grContent.node = self.node  # type: ignore
        self.grContent.setParentItem(self)

    def paint(self, painter, option: "QStyleOptionGraphicsItem", widget=None) -> None:
        """Paint the rounded rectangular node.

        Args:
            painter: QPainter to use
            QStyleOptionGraphicsItem: Style options
            widget: Widget being painted on
        """
        # Draw title background
        path_title = QPainterPath()
        path_title.setFillRule(Qt.FillRule.WindingFill)
        path_title.addRoundedRect(
            0, 0, self.width, self.title_height, self.edge_roundness, self.edge_roundness
        )
        path_title.addRect(0, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
        path_title.addRect(
            self.width - self.edge_roundness,
            self.title_height - self.edge_roundness,
            self.edge_roundness,
            self.edge_roundness,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # Draw content background
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
            self.width - self.edge_roundness, self.title_height, self.edge_roundness, self.edge_roundness
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # Draw outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(
            -1, -1, self.width + 2, self.height + 2, self.edge_roundness, self.edge_roundness
        )
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self.hovered:
            # Draw hover outline on top of default
            painter.setPen(self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
            painter.drawPath(path_outline.simplified())
