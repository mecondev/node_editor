"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
from PyQt5.QtCore import QByteArray, QDataStream, QIODevice, QMimeData, QPoint, QSize, Qt
from PyQt5.QtGui import QDrag, QIcon, QPixmap
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QListWidget, QListWidgetItem

from examples.calculator.calc_conf import CALC_NODES, LISTBOX_MIMETYPE, get_class_from_opcode
from node_editor.utils.helpers import dump_exception


class QDMDragListbox(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._press_pos = None
        self._drag_active = False
        self.init_ui()

    def init_ui(self):
        # init
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(False)  # Disable built-in drag; we use custom drag

        self.add_my_items()


    def add_my_items(self):
        keys = list(CALC_NODES.keys())
        keys.sort()
        for key in keys:
            node = get_class_from_opcode(key)
            self.add_my_item(node.op_title, node.icon, node.op_code)


    def add_my_item(self, name, icon=None, op_code=0):
        item = QListWidgetItem(name, self) # can be (icon, text, parent, <int>type)
        pixmap = QPixmap(icon if icon is not None else ".")
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole + 1, op_code)


    def mousePressEvent(self, event):
        """Record press position to apply drag threshold."""
        if event.button() == Qt.LeftButton:
            self._press_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Start drag only when moving enough distance and not already dragging."""
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
        try:
            item = self.currentItem()
            op_code = item.data(Qt.UserRole + 1)

            pixmap = QPixmap(item.data(Qt.UserRole))

            item_data = QByteArray()
            data_stream = QDataStream(item_data, QIODevice.WriteOnly)
            data_stream << pixmap
            data_stream.writeInt(op_code)
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
            self._press_pos = None

        except Exception as e:
            dump_exception(e)
