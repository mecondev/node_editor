"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit

from examples.calculator.calc_conf import OP_NODE_INPUT, register_node
from examples.calculator.calc_node_base import CalcGraphicsNode, CalcNode
from node_editor.utils.helpers import dump_exception
from node_editor.widgets.content_widget import QDMNodeContentWidget


class CalcInputContent(QDMNodeContentWidget):
    def init_ui(self):
        self.edit = QLineEdit("1", self)
        self.edit.setAlignment(Qt.AlignRight)
        self.edit.setObjectName(self.node.content_label_objname)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap=None):
        if hashmap is None:
            hashmap = {}
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            return True & res
        except Exception as e:
            dump_exception(e)
        return res


@register_node(OP_NODE_INPUT)
class CalcNodeInput(CalcNode):
    icon = "icons/in.png"
    op_code = OP_NODE_INPUT
    op_title = "Input"
    content_label_objname = "calc_node_input"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])
        self.graphics_node.setToolTip("Not evaluated yet")
        self.eval()  # noqa: A001

    def init_inner_classes(self):
        self.content = CalcInputContent(self)
        self.graphics_node = CalcGraphicsNode(self)
        self.content.edit.textChanged.connect(self.on_input_changed)

    def eval_implementation(self):
        u_value = self.content.edit.text()
        s_value = int(u_value)
        self.value = s_value
        self.mark_dirty(False)
        self.mark_invalid(False)

        self.mark_descendants_invalid(False)
        self.mark_descendants_dirty()

        self.graphics_node.setToolTip(f"Value: {self.value}")

        self.eval_children()

        return self.value
