"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

from examples.calculator.calc_conf import OP_NODE_OUTPUT, register_node
from examples.calculator.calc_node_base import CalcGraphicsNode, CalcNode
from node_editor.widgets.content_widget import QDMNodeContentWidget


class CalcOutputContent(QDMNodeContentWidget):
    def init_ui(self):
        self.lbl = QLabel("42", self)
        self.lbl.setAlignment(Qt.AlignLeft)
        self.lbl.setObjectName(self.node.content_label_objname)


@register_node(OP_NODE_OUTPUT)
class CalcNodeOutput(CalcNode):
    icon = "icons/out.png"
    op_code = OP_NODE_OUTPUT
    op_title = "Output"
    content_label_objname = "calc_node_output"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])

    def initInnerClasses(self):
        self.content = CalcOutputContent(self)
        self.graphics_node = CalcGraphicsNode(self)

    def evalImplementation(self):
        input_node = self.getInput(0)
        if not input_node:
            self.graphics_node.setToolTip("Input is not connected")
            self.mark_invalid()
            return

        val = input_node.eval()

        if val is None:
            self.graphics_node.setToolTip("Input is NaN")
            self.mark_invalid()
            return

        self.content.lbl.setText(f"{val}")
        self.mark_invalid(False)
        self.mark_dirty(False)
        self.graphics_node.setToolTip("")

        return val
