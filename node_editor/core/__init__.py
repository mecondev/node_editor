"""
Core module - Contains fundamental classes for the node editor.

Classes:
    - Serializable: Base class for serialization
    - Socket: Connection point on nodes
    - Node: Base node class (to be migrated)
    - Edge: Connection between sockets (to be migrated)
    - Scene: Container for nodes and edges (to be migrated)
"""

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
    from node_editor.graphics.socket import QDMGraphicsSocket

    Socket.Socket_GR_Class = QDMGraphicsSocket

_init_graphics_classes()

__all__ = [
    "Serializable",
    "Socket",
    "LEFT_TOP",
    "LEFT_CENTER",
    "LEFT_BOTTOM",
    "RIGHT_TOP",
    "RIGHT_CENTER",
    "RIGHT_BOTTOM",
]
