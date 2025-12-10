# -*- coding: utf-8 -*-
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
"""

__version__ = "1.0.0"
__author__ = ""

# Public API will be populated after migration
# Core classes
# from node_editor.core import Node, Edge, Socket, Scene

# Widgets
# from node_editor.widgets import NodeEditorWidget, NodeEditorWindow

# Node system
# from node_editor.nodes import BaseNode, NodeRegistry

# Theme engine
# from node_editor.themes import ThemeEngine

__all__ = [
    "__version__",
]
