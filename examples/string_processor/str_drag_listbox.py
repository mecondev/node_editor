"""String Processor - Drag and Drop Listbox.

Provides a listbox with draggable string processing nodes.

Author: Michael Economou
Date: 2025-12-14
"""

from PyQt5.QtCore import QByteArray, QDataStream, QIODevice, QMimeData, QPoint, QSize, Qt
from PyQt5.QtGui import QDrag, QIcon, QPainter, QPixmap
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QListWidget, QListWidgetItem

from examples.string_processor.str_conf import LISTBOX_MIMETYPE, STR_NODES, get_class_from_opcode
from node_editor.themes.theme_engine import ThemeEngine
from node_editor.utils.helpers import dump_exception


class StrDragListbox(QListWidget):
    """Listbox with draggable string processing nodes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._press_pos = None
        self._drag_active = False
        self.init_ui()

    def init_ui(self):
        """Initialize the listbox."""
        self.setIconSize(QSize(25, 25))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(False)  # Use custom drag

        self.add_my_items()

    def _load_svg_with_color(self, svg_path, color, size=32):
        """Load SVG and colorize it with the given color.

        Args:
            svg_path: Path to SVG file.
            color: QColor to apply to the SVG.
            size: Size of the resulting pixmap.

        Returns:
            QPixmap with the colorized SVG, or None on error.
        """
        try:
            # Read SVG file
            with open(svg_path) as f:
                svg_content = f.read()

            # Replace fill colors with the theme color
            color_hex = color.name()  # e.g., "#cccccc"

            # Replace common fill patterns in Material Design icons
            svg_content = svg_content.replace('fill="#000000"', f'fill="{color_hex}"')
            svg_content = svg_content.replace('fill="#000"', f'fill="{color_hex}"')
            svg_content = svg_content.replace('fill="black"', f'fill="{color_hex}"')
            svg_content = svg_content.replace('fill="#212121"', f'fill="{color_hex}"')

            # If no fill attribute, add one to the root svg element
            if 'fill=' not in svg_content:
                svg_content = svg_content.replace('<svg ', f'<svg fill="{color_hex}" ')

            # Render the modified SVG
            renderer = QSvgRenderer(QByteArray(svg_content.encode('utf-8')))
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            return pixmap
        except Exception as e:
            dump_exception(e)
            return None

    def add_my_items(self):
        """Add all registered nodes to the listbox."""
        keys = list(STR_NODES.keys())
        keys.sort()
        for key in keys:
            node = get_class_from_opcode(key)
            self.add_my_item(node.op_title, node.icon, node.op_code)

    def add_my_item(self, name, icon=None, op_code=0):
        """Add an item to the listbox.

        Args:
            name: Display name for the node.
            icon: Path to icon file (SVG).
            op_code: Operation code for the node.
        """
        item = QListWidgetItem(name, self)

        # Get icon color from theme
        theme = ThemeEngine.current_theme()
        icon_color = theme.icon_color

        # Load SVG icon with theme color
        if icon and icon.endswith('.svg'):
            pixmap = self._load_svg_with_color(icon, icon_color, 32)
            if pixmap:
                item.setIcon(QIcon(pixmap))
        elif icon:
            pixmap = QPixmap(icon)
            item.setIcon(QIcon(pixmap))
        else:
            pixmap = QPixmap(".")
            item.setIcon(QIcon(pixmap))

        item.setSizeHint(QSize(32, 32))
        item.setText(name)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # Store data
        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole + 1, op_code)

    def mousePressEvent(self, event):
        """Record press position for drag threshold."""
        if event.button() == Qt.LeftButton:
            self._press_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Start drag when moving enough distance."""
        if (
            not self._drag_active
            and self._press_pos is not None
            and event.buttons() & Qt.LeftButton
            and (event.pos() - self._press_pos).manhattanLength() >= QApplication.startDragDistance()
        ):
            self.start_drag()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Reset drag state on release."""
        self._press_pos = None
        super().mouseReleaseEvent(event)

    def start_drag(self):
        """Start dragging the selected item."""
        try:
            item = self.currentItem()
            op_code = item.data(Qt.UserRole + 1)

            pixmap = QPixmap(item.data(Qt.UserRole))

            item_data = QByteArray()
            data_stream = QDataStream(item_data, QIODevice.WriteOnly)
            data_stream << pixmap
            data_stream.writeInt32(op_code)
            data_stream.writeQString(item.text())

            mime_data = QMimeData()
            mime_data.setData(LISTBOX_MIMETYPE, item_data)

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
            drag.setPixmap(pixmap)

            self._drag_active = True
            drag.exec_(Qt.MoveAction)
            self._drag_active = False

        except Exception as e:
            dump_exception(e)
