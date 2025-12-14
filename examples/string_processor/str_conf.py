"""String Processor Node Editor - Configuration.

Op codes and node registration for string processing nodes.

Author: Michael Economou
Date: 2025-12-14
"""

LISTBOX_MIMETYPE = "application/x-item"

# Op codes for string processor nodes (200-219)
OP_NODE_TEXT_INPUT = 201
OP_NODE_TEXT_OUTPUT = 202
OP_NODE_CONCAT = 203
OP_NODE_FORMAT = 204
OP_NODE_LENGTH = 205
OP_NODE_SUBSTRING = 206
OP_NODE_SPLIT = 207

# Node registry
STR_NODES = {}


class ConfError(Exception):
    """Configuration exception base class."""


class InvalidNodeRegistrationError(ConfError):
    """Raised when node registration is invalid."""


class OpCodeNotRegisteredError(ConfError):
    """Raised when opcode is not registered."""


def register_node_now(op_code, class_reference):
    """Register a node class with an op code."""
    if op_code in STR_NODES:
        raise InvalidNodeRegistrationError(
            f"Duplicate node registration of '{op_code}'. "
            f"There is already {STR_NODES[op_code]}"
        )
    STR_NODES[op_code] = class_reference


def register_node(op_code):
    """Decorator to register a node class."""
    def decorator(original_class):
        register_node_now(op_code, original_class)
        return original_class
    return decorator


def get_class_from_opcode(op_code):
    """Get node class from op code."""
    if op_code not in STR_NODES:
        raise OpCodeNotRegisteredError(f"OpCode '{op_code}' is not registered")
    return STR_NODES[op_code]


# Import all nodes and register them
from examples.string_processor.nodes import *
