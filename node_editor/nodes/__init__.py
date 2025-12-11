"""Node system with registry and base classes.

This module provides the node type registration system and base classes
for creating custom nodes in the node editor.

Classes:
    BaseNode: Base class for creating custom node types.
    NodeRegistry: Central registry for node type management.

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
from node_editor.nodes.registry import NodeRegistry

__all__ = [
    "NodeRegistry",
    "BaseNode",
]
