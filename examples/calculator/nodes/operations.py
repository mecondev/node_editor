"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
import os

from examples.calculator.calc_conf import (
    OP_NODE_ADD,
    OP_NODE_DIV,
    OP_NODE_MUL,
    OP_NODE_SUB,
    register_node,
)
from examples.calculator.calc_node_base import CalcNode


def get_icon_path(relative_path):
    """Get absolute path for icon file."""
    return os.path.join(os.path.dirname(__file__), "..", relative_path)


@register_node(OP_NODE_ADD)
class CalcNodeAdd(CalcNode):
    icon = get_icon_path("icons/add.png")
    op_code = OP_NODE_ADD
    op_title = "Add"
    content_label = "+"
    content_label_objname = "calc_node_bg"

    def eval_operation(self, input1, input2):
        return input1 + input2


@register_node(OP_NODE_SUB)
class CalcNodeSub(CalcNode):
    icon = get_icon_path("icons/sub.png")
    op_code = OP_NODE_SUB
    op_title = "Substract"
    content_label = "-"
    content_label_objname = "calc_node_bg"

    def eval_operation(self, input1, input2):
        return input1 - input2

@register_node(OP_NODE_MUL)
class CalcNodeMul(CalcNode):
    icon = get_icon_path("icons/mul.png")
    op_code = OP_NODE_MUL
    op_title = "Multiply"
    content_label = "*"
    content_label_objname = "calc_node_mul"

    def eval_operation(self, input1, input2):
        return input1 * input2

@register_node(OP_NODE_DIV)
class CalcNodeDiv(CalcNode):
    icon = get_icon_path("icons/divide.png")
    op_code = OP_NODE_DIV
    op_title = "Divide"
    content_label = "/"
    content_label_objname = "calc_node_div"

    def eval_operation(self, input1, input2):
        if input2 == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return input1 / input2

# way how to register by function call
# register_node_now(OP_NODE_ADD, CalcNode_Add)
