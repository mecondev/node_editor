"""Node system with registry and base classes.

This module provides the node type registration system and base classes
for creating custom nodes in the node editor.

Classes:
    BaseNode: Base class for creating custom node types.
    NodeRegistry: Central registry for node type management.

Built-in Nodes (Core - Op Codes 1-30):
    NumberInputNode, TextInputNode: Input nodes for user data entry.
    OutputNode: Display node for showing results.
    AddNode, SubtractNode, MultiplyNode, DivideNode: Basic math operations.
    EqualNode, NotEqualNode, LessThanNode, etc: Comparison operations.
    IfNode: Conditional switch node.

Extended Nodes (Op Codes 40+):
    String Operations (40-49): Concatenate, Format, Length, Substring, Split.
    Math Extended (50-59): Power, Sqrt, Abs, Min, Max, Round, Modulo.
    Logic Extended (60-69): AND, OR, NOT, XOR.
    Conversion Nodes (70-79): ToString, ToNumber, ToBool, ToInt.
    Utility Nodes (80-89): Constant, Print, Comment, Clamp, Random.
    List Operations (90-99): CreateList, GetItem, ListLength, Append, Join.

Usage:
    Create and register a custom node::

        from node_editor.nodes import BaseNode, NodeRegistry

        @NodeRegistry.register(100)
        class MyNode(BaseNode):
            op_title = "My Custom Node"
            category = "Custom"

Author:
    Michael Economou

Date:
    2025-12-11
"""

from node_editor.nodes.base import BaseNode
from node_editor.nodes.conversion_nodes import (
    ToBoolNode,
    ToIntNode,
    ToNumberNode,
    ToStringNode,
)

# Import built-in node types to auto-register them
from node_editor.nodes.input_node import NumberInputNode, TextInputNode
from node_editor.nodes.list_nodes import (
    AppendNode,
    CreateListNode,
    GetItemNode,
    JoinNode,
    ListLengthNode,
)
from node_editor.nodes.logic_nodes import (
    AndNode,
    EqualNode,
    GreaterEqualNode,
    GreaterThanNode,
    IfNode,
    LessEqualNode,
    LessThanNode,
    NotEqualNode,
    NotNode,
    OrNode,
    XorNode,
)
from node_editor.nodes.math_nodes import (
    AbsNode,
    AddNode,
    DivideNode,
    MaxNode,
    MinNode,
    ModuloNode,
    MultiplyNode,
    PowerNode,
    RoundNode,
    SqrtNode,
    SubtractNode,
)
from node_editor.nodes.output_node import OutputNode
from node_editor.nodes.registry import NodeRegistry

# Import extended node types
from node_editor.nodes.string_nodes import (
    ConcatenateNode,
    FormatNode,
    LengthNode,
    SplitNode,
    SubstringNode,
)
from node_editor.nodes.utility_nodes import (
    ClampNode,
    CommentNode,
    ConstantNode,
    PrintNode,
    RandomNode,
)

__all__ = [
    "NodeRegistry",
    "BaseNode",
    # Input nodes
    "NumberInputNode",
    "TextInputNode",
    # Output nodes
    "OutputNode",
    # Math nodes
    "AddNode",
    "SubtractNode",
    "MultiplyNode",
    "DivideNode",
    # Logic nodes
    "EqualNode",
    "NotEqualNode",
    "LessThanNode",
    "LessEqualNode",
    "GreaterThanNode",
    "GreaterEqualNode",
    "IfNode",
    # String operations
    "ConcatenateNode",
    "FormatNode",
    "LengthNode",
    "SubstringNode",
    "SplitNode",
    # Math extended
    "PowerNode",
    "SqrtNode",
    "AbsNode",
    "MinNode",
    "MaxNode",
    "RoundNode",
    "ModuloNode",
    # Logic extended
    "AndNode",
    "OrNode",
    "NotNode",
    "XorNode",
    # Conversion nodes
    "ToStringNode",
    "ToNumberNode",
    "ToBoolNode",
    "ToIntNode",
    # Utility nodes
    "ConstantNode",
    "PrintNode",
    "CommentNode",
    "ClampNode",
    "RandomNode",
    # List operations
    "CreateListNode",
    "GetItemNode",
    "ListLengthNode",
    "AppendNode",
    "JoinNode",
]
