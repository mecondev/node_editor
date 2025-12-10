"""
Graphics module - Qt Graphics classes for visual representation.

Classes:
    - QDMGraphicsSocket: Visual representation of sockets
    - QDMGraphicsNode: Visual representation of nodes
    - QDMGraphicsView: Custom QGraphicsView with zoom and pan (to be migrated)
    - QDMGraphicsScene: Custom QGraphicsScene with grid (to be migrated)
    - QDMGraphicsEdge: Visual representation of edges (to be migrated)
    - QDMGraphicsCutLine: Line for cutting edges (to be migrated)
"""

from node_editor.graphics.node import QDMGraphicsNode
from node_editor.graphics.socket import QDMGraphicsSocket

__all__ = [
    "QDMGraphicsSocket",
    "QDMGraphicsNode",
]

# Will be populated after migration
# from node_editor.graphics.view import QDMGraphicsView
# from node_editor.graphics.scene import QDMGraphicsScene
# from node_editor.graphics.edge import QDMGraphicsEdge
# from node_editor.graphics.cutline import QDMGraphicsCutLine


__all__ = []
