"""
Node Editor - A portable PyQt5 node-based visual programming framework.

Usage:
    from node_editor import NodeEditorWidget, NodeEditorWindow
    from node_editor.nodes import BaseNode, NodeRegistry
    from node_editor.themes import ThemeEngine

Example:
    # Embed in your application
    from node_editor import NodeEditorWidget

    widget = NodeEditorWidget(parent)
    layout.addWidget(widget)

    # Create custom nodes
    from node_editor.nodes import BaseNode, NodeRegistry

    @NodeRegistry.register(100)
    class MyNode(BaseNode):
        op_title = "My Custom Node"
        ...

Author: Michael Economou
Date: 2025-12-11
"""

__version__ = "1.0.0"
__author__ = ""

# Initialize graphics class bindings (must be done before using widgets)
from node_editor.core import _init_graphics_classes

_init_graphics_classes()

# Public API
# Core classes
from node_editor.core import Edge, Node, Socket

# Node system
from node_editor.nodes import BaseNode, NodeRegistry

# Theme engine
from node_editor.themes import ThemeEngine

# Widgets
from node_editor.widgets import NodeEditorWidget, NodeEditorWindow

__all__ = [
    "__version__",
    # Core
    "Node",
    "Edge",
    "Socket",
    # Widgets
    "NodeEditorWidget",
    "NodeEditorWindow",
    # Nodes
    "BaseNode",
    "NodeRegistry",
    # Themes
    "ThemeEngine",
]
