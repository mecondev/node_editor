"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

from examples.calculator.calc_conf import OP_NODE_OUTPUT, register_node
from examples.calculator.calc_node_base import CalcGraphicsNode, CalcNode
from node_editor.widgets.content_widget import QDMNodeContentWidget


def get_icon_path(relative_path):
    """Get absolute path for icon file."""
    return os.path.join(os.path.dirname(__file__), "..", relative_path)


def format_number(value):
    """Format number with smart decimal handling.

    Rules:
    - Integer values show without decimals (2.0 -> 2)
    - Decimals up to 10 total digits with rounding (20/3 -> 6.666666667)
    - Very large/small numbers use exponential notation
    """
    if not isinstance(value, int | float):
        return str(value)

    # Check if it's effectively an integer (including Python int type)
    if isinstance(value, int) or (isinstance(value, float) and value == int(value)):
        return str(int(value))

    # Handle very large or very small numbers with exponential notation
    abs_value = abs(value)
    if abs_value >= 1e10 or (abs_value < 1e-4 and abs_value != 0):
        return f"{value:.4e}"

    # Format with up to 10 total significant digits (for non-integer floats)
    # Calculate how many decimal places we can afford
    if abs_value >= 1:
        int_digits = len(str(int(abs_value)))
        decimal_places = max(1, 10 - int_digits)  # At least 1 decimal for floats
    else:
        decimal_places = 9

    formatted = f"{value:.{decimal_places}f}"
    # Strip trailing zeros after decimal point
    if '.' in formatted:
        formatted = formatted.rstrip('0').rstrip('.')

    return formatted


@register_node(OP_NODE_OUTPUT)
class CalcNodeOutput(CalcNode):
    """Node for displaying output values."""
    icon = get_icon_path("icons/out.png")
    op_code = OP_NODE_OUTPUT
    op_title = "Output"
    content_label_objname = "calc_node_output"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])
        self.graphics_node.setToolTip("Not connected")

    def init_inner_classes(self):
        self.content = CalcOutputContent(self)
        self.graphics_node = CalcGraphicsNode(self)

    def eval_implementation(self):
        input_node = self.get_input(0)
        if not input_node:
            self.content.lbl.setText("--")
            self.graphics_node.setToolTip("Input is not connected")
            self.mark_dirty()
            self.mark_invalid(False)
            return

        # If upstream node is already invalid, avoid calling eval() again.
        # This prevents stale values and avoids recursion when upstream nodes
        # propagate evaluation to children on errors.
        if input_node.is_invalid():
            self.content.lbl.setText("--")
            self.graphics_node.setToolTip("Input has an error")
            self.mark_dirty()
            self.mark_invalid(False)
            return

        val = input_node.eval()

        if val is None:
            self.content.lbl.setText("--")
            self.graphics_node.setToolTip("Input is invalid")
            self.mark_dirty()
            self.mark_invalid(False)
            return

        formatted_val = format_number(val)
        self.content.lbl.setText(formatted_val)
        self.mark_invalid(False)
        self.mark_dirty(False)
        self.graphics_node.setToolTip(f"Output: {formatted_val}")

        return val


class CalcOutputContent(QDMNodeContentWidget):
    """Content widget for output node."""

    def init_ui(self):
        """Initialize UI with a label for displaying results."""
        self.lbl = QLabel("--", self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setObjectName(self.node.content_label_objname)
        self.lbl.setFixedWidth(184)  # Match node width minus padding
