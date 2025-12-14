"""String Processor - Text Input Node.

Provides text input field for entering string values.

Author: Michael Economou
Date: 2025-12-14
"""

from PyQt5.QtWidgets import QLineEdit, QVBoxLayout

from examples.string_processor.str_conf import OP_NODE_TEXT_INPUT, register_node
from examples.string_processor.str_node_base import (
    StrGraphicsNode,
    StrNode,
    get_icon_path,
)
from node_editor.core.socket import RIGHT_CENTER
from node_editor.widgets.content_widget import QDMNodeContentWidget


class StrTextInputContent(QDMNodeContentWidget):
    """Content widget with text input field."""

    def init_ui(self):
        """Initialize the text input field."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        self.setLayout(layout)

        self.edit = QLineEdit("", self)
        self.edit.setObjectName("str_input_edit")
        self.edit.textChanged.connect(self.on_value_changed)
        layout.addWidget(self.edit)

    def on_value_changed(self):
        """Handle value changes and trigger node evaluation."""
        if hasattr(self.node, 'mark_dirty'):
            self.node.mark_dirty()
        if hasattr(self.node, 'eval'):
            self.node.eval()

    def serialize(self):
        """Serialize the input value."""
        res = super().serialize()
        res['value'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap=None):
        """Restore the input value."""
        if hashmap is None:
            hashmap = {}
        res = super().deserialize(data, hashmap)
        if "value" in data:
            self.edit.setText(data["value"])
        return True and res


@register_node(OP_NODE_TEXT_INPUT)
class StrTextInput(StrNode):
    """Node for text input.

    Allows user to enter string values into the graph.

    Op Code: 201
    Inputs: None
    Outputs: 1 (string value)
    """

    icon = get_icon_path("icons/text_in.svg")
    op_code = OP_NODE_TEXT_INPUT
    op_title = "Text Input"
    content_label = ""
    content_label_objname = "str_input_node"

    _graphics_node_class = StrGraphicsNode
    _content_widget_class = StrTextInputContent

    def __init__(self, scene):
        """Create a text input node.

        Args:
            scene: Parent scene containing this node.
        """
        super().__init__(scene, inputs=[], outputs=[5])
        self.value = ""
        self.mark_dirty()

    def init_settings(self):
        """Configure socket positions."""
        super().init_settings()
        self.output_socket_position = RIGHT_CENTER

    def eval_implementation(self):
        """Return the text value from the input field."""
        self.value = self.content.edit.text()
        self.mark_dirty(False)
        self.mark_invalid(False)
        self.graphics_node.setToolTip(f"Text: {self.value!r}")

        self.mark_descendants_dirty()
        self.eval_children()

        return self.value
