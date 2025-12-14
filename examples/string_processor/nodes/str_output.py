"""String Processor - Text Output Node.

Displays string output values.

Author: Michael Economou
Date: 2025-12-14
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout

from examples.string_processor.str_conf import OP_NODE_TEXT_OUTPUT, register_node
from examples.string_processor.str_node_base import (
    StrGraphicsNode,
    StrNode,
    get_icon_path,
)
from node_editor.core.socket import LEFT_CENTER
from node_editor.widgets.content_widget import QDMNodeContentWidget


class StrTextOutputContent(QDMNodeContentWidget):
    """Content widget with result display label."""

    def init_ui(self):
        """Initialize the output display label."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        self.setLayout(layout)

        self.label = QLabel("--", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("str_output_label")
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(160)
        layout.addWidget(self.label)

    def set_value(self, value):
        """Update the displayed value.

        Args:
            value: Value to display (will be converted to string).
        """
        if value is None:
            self.label.setText("--")
        else:
            text = str(value)
            # Truncate if too long
            if len(text) > 50:
                text = text[:47] + "..."
            self.label.setText(text)


@register_node(OP_NODE_TEXT_OUTPUT)
class StrTextOutput(StrNode):
    """Node for displaying string results.

    Shows the value from a connected input node.

    Op Code: 202
    Inputs: 1 (string value)
    Outputs: None
    """

    icon = get_icon_path("icons/text_out.svg")
    op_code = OP_NODE_TEXT_OUTPUT
    op_title = "Text Output"
    content_label = ""
    content_label_objname = "str_output_node"

    _graphics_node_class = StrGraphicsNode
    _content_widget_class = StrTextOutputContent

    def __init__(self, scene):
        """Create a text output node.

        Args:
            scene: Parent scene containing this node.
        """
        super().__init__(scene, inputs=[5], outputs=[])

    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        return res

    def deserialize(self, data, hashmap=None, restore_id=True):
        if hashmap is None:
            hashmap = {}
        res = super().deserialize(data, hashmap, restore_id)
        self.value = None
        self.mark_dirty()
        return res

    def init_settings(self):
        """Configure socket positions."""
        super().init_settings()
        self.input_socket_position = LEFT_CENTER

    def eval_implementation(self):
        """Display the input value."""
        input_node = self.get_input(0)

        if input_node is None:
            self.value = None
            self.mark_invalid()
            self.content.set_value(None)
            self.graphics_node.setToolTip("Connect input")
            return None

        # Call eval() on the input node to get its value
        input_val = input_node.eval()
        self.value = str(input_val) if input_val is not None else None
        self.mark_dirty(False)
        self.mark_invalid(False)
        self.content.set_value(self.value)
        self.graphics_node.setToolTip(f"Output: {self.value!r}")

        return self.value
