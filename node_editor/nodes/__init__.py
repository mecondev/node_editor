"""
Nodes module - Node system with registry and built-in nodes.

Classes:
    - BaseNode: Base class for creating custom nodes
    - NodeRegistry: Central registry for node types

Built-in Nodes:
    - InputNode: Number/text input
    - OutputNode: Display output
    - AddNode, SubNode, MulNode, DivNode: Math operations
    - CompareNode: Comparison operations

Author: Michael Economou
Date: 2025-12-11
"""

from node_editor.nodes.base import BaseNode
from node_editor.nodes.registry import NodeRegistry

__all__ = [
    "NodeRegistry",
    "BaseNode",
]
