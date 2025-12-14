"""String Processor - Base Node Classes.

Base classes for string processing nodes with common styling and behavior.

Author: Michael Economou
Date: 2025-12-14
"""

import logging
import os

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QLabel

from node_editor.core.node import Node
from node_editor.core.socket import LEFT_CENTER, RIGHT_CENTER
from node_editor.graphics.node import QDMGraphicsNode
from node_editor.widgets.content_widget import QDMNodeContentWidget

logger = logging.getLogger(__name__)


class StrGraphicsNode(QDMGraphicsNode):
    """Graphics node for string processor input/output nodes."""

    def init_sizes(self):
        """Initialize size parameters."""
        super().init_sizes()
        self.width = 180
        self.height = 74
        self.edge_roundness = 6
        self.edge_padding = 0
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10

    def init_assets(self):
        """Initialize status icons."""
        super().init_assets()
        base_dir = os.path.dirname(__file__)
        local_path = os.path.join(base_dir, "icons", "status_icons.png")
        calc_path = os.path.join(base_dir, "..", "..", "calculator", "icons", "status_icons.png")
        for candidate in (local_path, calc_path):
            if os.path.exists(candidate):
                self.icons = QImage(candidate)
                break
        else:
            self.icons = None

    def paint(self, painter, option, widget=None):
        """Paint the node with status indicator."""
        super().paint(painter, option, widget)

        if self.icons is None:
            return

        offset = 24.0
        if self.node.is_dirty():
            offset = 0.0
        if self.node.is_invalid():
            offset = 48.0

        painter.drawImage(
            QRectF(-10, -10, 24.0, 24.0),
            self.icons,
            QRectF(offset, 0, 24.0, 24.0)
        )


class StrOpGraphicsNode(StrGraphicsNode):
    """Graphics node for operation nodes (compact 2:1 ratio)."""

    def init_sizes(self):
        """Initialize size parameters for operation nodes."""
        super().init_sizes()
        self.width = 150
        self.height = 74


class StrContent(QDMNodeContentWidget):
    """Content widget with operation label."""

    def init_ui(self):
        """Initialize the content label."""
        lbl = QLabel(self.node.content_label, self)
        lbl.setObjectName(self.node.content_label_objname)


class StrNode(Node):
    """Base class for string operation nodes."""

    icon = ""
    op_code = 0
    op_title = "String Operation"
    content_label = ""
    content_label_objname = "str_node_bg"

    _graphics_node_class = StrGraphicsNode
    _content_widget_class = StrContent

    def __init__(self, scene, inputs=None, outputs=None):
        """Initialize string node.

        Args:
            scene: Parent scene containing this node.
            inputs: Input socket configuration.
            outputs: Output socket configuration.
        """
        if inputs is None:
            inputs = [5, 5]  # String sockets
        if outputs is None:
            outputs = [5]
        super().__init__(scene, self.__class__.op_title, inputs, outputs)

        self.value = None
        self.graphics_node.setToolTip("Not evaluated yet")
        self.mark_dirty()

    def init_settings(self):
        """Configure socket positions."""
        super().init_settings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def eval(self, _index=0):
        """Evaluate this node and return its value.

        Args:
            _index: Output socket index (unused).

        Returns:
            The computed value or cached value if clean.
        """
        if not self.is_dirty() and not self.is_invalid():
            logger.debug("Returning cached %s value: %r", self.__class__.__name__, self.value)
            return self.value

        try:
            val = self.eval_implementation()
            return val
        except Exception as e:
            self.value = None
            self.mark_invalid()
            self.graphics_node.setToolTip(str(e))
            self.mark_descendants_dirty()
            self.eval_children()
            logger.error("%s eval error: %s", self.__class__.__name__, e)
            return None

    def eval_operation(self, *_args):
        """Perform the string operation. Override in subclasses.

        Args:
            *args: Input values.

        Returns:
            Result of the operation.
        """
        return ""

    def eval_implementation(self):
        """Evaluate the node operation."""
        # Get input values by calling eval() on connected nodes
        inputs = []
        for i in range(len(self.inputs)):
            input_node = self.get_input(i)
            if input_node is None:
                self.value = None
                self.mark_invalid()
                self.mark_descendants_dirty()
                self.graphics_node.setToolTip(f"Connect input {i+1}")
                self.eval_children()
                return None
            # Call eval() on the input node to get its value
            input_val = input_node.eval()
            inputs.append(input_val)

        # Perform operation
        try:
            self.value = self.eval_operation(*inputs)
            self.mark_dirty(False)
            self.mark_invalid(False)
            self.graphics_node.setToolTip(f"{self.op_title}: {self.value!r}")
            self.mark_descendants_dirty()
            self.eval_children()
            return self.value
        except Exception as e:
            self.value = None
            self.mark_invalid()
            self.graphics_node.setToolTip(f"Error: {e}")
            logger.error("%s eval error: %s", self.op_title, e)
            return None

    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        return res

    def deserialize(self, data, hashmap=None, restore_id=True):
        if hashmap is None:
            hashmap = {}
        res = super().deserialize(data, hashmap, restore_id)
        return res


def get_icon_path(relative_path):
    """Get absolute path for icon file.

    Args:
        relative_path: Relative path from this file (e.g., "icons/concat.svg").

    Returns:
        Absolute path to the icon file.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), relative_path))
