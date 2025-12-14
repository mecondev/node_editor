"""String Processor - Sub Window.

Sub-window for string processor node editor (single canvas version).

Author: Michael Economou
Date: 2025-12-14
"""

import logging

from examples.string_processor.str_conf import (
    LISTBOX_MIMETYPE,
    get_class_from_opcode,
)
from node_editor.utils.helpers import dump_exception
from node_editor.widgets.editor_widget import NodeEditorWidget

logger = logging.getLogger(__name__)


class StrSubWindow(NodeEditorWidget):
    """Sub-window for string processor node editor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(0x80)  # Qt.WA_DeleteOnClose

        self.setTitle()

        # Setup listeners after parent init
        self.scene.add_has_been_modified_listener(self.setTitle)
        self.scene.history.add_history_restored_listener(self.on_history_restored)
        # Add drag/drop listeners directly to the view
        self.view.add_drag_enter_listener(self.on_drag_enter)
        self.view.add_drop_listener(self.on_drop)
        self.scene.set_node_class_selector(self.get_node_class_from_data)

    def setTitle(self):
        """Set window title."""
        self.setWindowTitle(self.get_user_friendly_filename())

    def get_node_class_from_data(self, data):
        """Get node class from serialized data."""
        if 'op_code' not in data:
            from node_editor.core.node import Node
            return Node
        return get_class_from_opcode(data['op_code'])

    def file_load(self, filename):
        """Load scene from file."""
        if super().file_load(filename):
            self.setTitle()
            self.do_eval_outputs()
            return True
        return False

    def do_eval_outputs(self):
        """Force evaluation of all nodes after load."""
        # First mark all input nodes dirty and evaluate them
        for node in self.scene.nodes:
            if node.__class__.__name__ == "StrTextInput":
                node.mark_dirty()
                node.eval()

        # Then evaluate all other nodes including outputs
        for node in self.scene.nodes:
            if node.__class__.__name__ != "StrTextInput":
                node.mark_dirty()
                node.eval()

    def on_history_restored(self):
        """Handle history restore event."""
        self.setTitle()

    def on_drag_enter(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            event.setAccepted(False)

    def on_drop(self, event):
        """Handle drop event to create node."""
        if not event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.ignore()
            return

        event_data = event.mimeData().data(LISTBOX_MIMETYPE)
        data_stream = event_data

        from PyQt5.QtCore import QByteArray, QDataStream, QIODevice
        from PyQt5.QtGui import QPixmap
        byte_array = QByteArray(event_data)
        data_stream = QDataStream(byte_array, QIODevice.ReadOnly)

        pixmap = QPixmap()
        data_stream >> pixmap
        op_code = data_stream.readInt32()
        text = data_stream.readQString()

        mouse_pos = event.pos()
        scene_pos = self.view.mapToScene(mouse_pos)

        logger.debug("Dropping node: op_code=%s, text=%s at %s", op_code, text, scene_pos)

        try:
            node = get_class_from_opcode(op_code)(self.scene)
            logger.debug("Setting pos for node: %s", node)
            node.set_pos(scene_pos.x(), scene_pos.y())
            self.scene.history.store_history(f"Created node {node.__class__.__name__}")
        except Exception as e:
            dump_exception(e)

        event.setDropAction(0x1)  # Qt.MoveAction
        event.accept()
