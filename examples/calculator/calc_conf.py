"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
LISTBOX_MIMETYPE = "application/x-item"

OP_NODE_INPUT = 1
OP_NODE_OUTPUT = 2
OP_NODE_ADD = 3
OP_NODE_SUB = 4
OP_NODE_MUL = 5
OP_NODE_DIV = 6


CALC_NODES = {
}


class ConfError(Exception):
    """Configuration exception base class."""


class InvalidNodeRegistrationError(ConfError):
    """Raised when node registration is invalid."""


class OpCodeNotRegisteredError(ConfError):
    """Raised when opcode is not registered."""


def register_node_now(op_code, class_reference):
    if op_code in CALC_NODES:
        raise InvalidNodeRegistrationError(
            f"Duplicate node registration of '{op_code}'. "
            f"There is already {CALC_NODES[op_code]}"
        )
    CALC_NODES[op_code] = class_reference


def register_node(op_code):
    def decorator(original_class):
        register_node_now(op_code, original_class)
        return original_class
    return decorator

def get_class_from_opcode(op_code):
    if op_code not in CALC_NODES:
        raise OpCodeNotRegisteredError(f"OpCode '{op_code}' is not registered")
    return CALC_NODES[op_code]



# import all nodes and register them
from examples.calculator.nodes import *
