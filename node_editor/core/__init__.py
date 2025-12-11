"""
Core module - Contains fundamental classes for the node editor.

Classes:
    - Serializable: Base class for serialization
    - Socket: Connection point on nodes
    - Node: Base node class
    - Edge: Connection between sockets
    - Scene: Container for nodes and edges (to be migrated)

Author: Michael Economou
Date: 2025-12-11
"""

from node_editor.core.edge import (
    EDGE_TYPE_BEZIER,
    EDGE_TYPE_DEFAULT,
    EDGE_TYPE_DIRECT,
    EDGE_TYPE_IMPROVED_BEZIER,
    EDGE_TYPE_IMPROVED_SHARP,
    EDGE_TYPE_SQUARE,
    Edge,
)
from node_editor.core.node import Node
from node_editor.core.serializable import Serializable
from node_editor.core.socket import (
    LEFT_BOTTOM,
    LEFT_CENTER,
    LEFT_TOP,
    RIGHT_BOTTOM,
    RIGHT_CENTER,
    RIGHT_TOP,
    Socket,
)


# Late binding for graphics classes to avoid circular imports
def _init_graphics_classes():
    """Initialize graphics class references."""
    from node_editor.graphics.edge import QDMGraphicsEdge
    from node_editor.graphics.node import QDMGraphicsNode
    from node_editor.graphics.socket import QDMGraphicsSocket
    from node_editor.widgets.content_widget import QDMNodeContentWidget

    Socket.Socket_GR_Class = QDMGraphicsSocket
    Node.GraphicsNode_class = QDMGraphicsNode
    Node.NodeContent_class = QDMNodeContentWidget
    Edge.GraphicsEdge_class = QDMGraphicsEdge


# NOTE: Graphics classes are initialized lazily on first use
# to avoid circular import issues at module initialization time
# _init_graphics_classes()

__all__ = [
    "Serializable",
    "Socket",
    "Node",
    "Edge",
    "LEFT_TOP",
    "LEFT_CENTER",
    "LEFT_BOTTOM",
    "RIGHT_TOP",
    "RIGHT_CENTER",
    "RIGHT_BOTTOM",
    "EDGE_TYPE_DIRECT",
    "EDGE_TYPE_BEZIER",
    "EDGE_TYPE_SQUARE",
    "EDGE_TYPE_IMPROVED_SHARP",
    "EDGE_TYPE_IMPROVED_BEZIER",
    "EDGE_TYPE_DEFAULT",
]
