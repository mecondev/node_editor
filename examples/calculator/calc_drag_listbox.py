"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
from PyQt5.QtCore import QByteArray, QDataStream, QIODevice, QMimeData, QPoint, QSize, Qt
from PyQt5.QtGui import QDrag, QIcon, QPixmap
from PyQt5.QtWidgets import QAbstractItemView, QListWidget, QListWidgetItem

from examples.calculator.calc_conf import CALC_NODES, LISTBOX_MIMETYPE, get_class_from_opcode
from node_editor.utils.helpers import dump_exception


class QDMDragListbox(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # init
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.addMyItems()


    def addMyItems(self):
        keys = list(CALC_NODES.keys())
        keys.sort()
        for key in keys:
            node = get_class_from_opcode(key)
            self.addMyItem(node.op_title, node.icon, node.op_code)


    def addMyItem(self, name, icon=None, op_code=0):
        item = QListWidgetItem(name, self) # can be (icon, text, parent, <int>type)
        pixmap = QPixmap(icon if icon is not None else ".")
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole + 1, op_code)


    def startDrag(self, _event=None):
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

            drag.exec_(Qt.MoveAction)

        except Exception as e:
            dump_exception(e)
