"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
from examples.calculator.calc_conf import (
    OP_NODE_ADD,
    OP_NODE_DIV,
    OP_NODE_MUL,
    OP_NODE_SUB,
    register_node,
)
from examples.calculator.calc_node_base import CalcNode


@register_node(OP_NODE_ADD)
class CalcNodeAdd(CalcNode):
    icon = "icons/add.png"
    op_code = OP_NODE_ADD
    op_title = "Add"
    content_label = "+"
    content_label_objname = "calc_node_bg"

    def eval_operation(self, input1, input2):
        return input1 + input2


@register_node(OP_NODE_SUB)
class CalcNodeSub(CalcNode):
    icon = "icons/sub.png"
    op_code = OP_NODE_SUB
    op_title = "Substract"
    content_label = "-"
    content_label_objname = "calc_node_bg"

    def eval_operation(self, input1, input2):
        return input1 - input2

@register_node(OP_NODE_MUL)
class CalcNodeMul(CalcNode):
    icon = "icons/mul.png"
    op_code = OP_NODE_MUL
    op_title = "Multiply"
    content_label = "*"
    content_label_objname = "calc_node_mul"

    def eval_operation(self, input1, input2):
        print('foo')
        return input1 * input2

@register_node(OP_NODE_DIV)
class CalcNodeDiv(CalcNode):
    icon = "icons/divide.png"
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
