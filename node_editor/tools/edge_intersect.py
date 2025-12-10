"""
Edge Intersect - Node dropping on edges to insert nodes.

This module handles the functionality where a node can be dropped onto
an existing edge to automatically insert it between the connected nodes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5.QtCore import QRectF

if TYPE_CHECKING:
    from node_editor.core.edge import Edge
    from node_editor.core.node import Node
    from node_editor.graphics.view import QDMGraphicsView


class EdgeIntersect:
    """Handles node dropping on edges to create automatic connections.

    When a node is dragged and dropped on an existing edge, this class
    automatically splits the edge and connects the dropped node in between.

    Attributes:
        grScene: Reference to the QDMGraphicsScene
        grView: Reference to the QDMGraphicsView
        draggedNode: Node currently being dragged
        hoveredList: List of graphics items being hovered over
    """

    def __init__(self, gr_view: QDMGraphicsView) -> None:
        """Initialize edge intersect.

        Args:
            gr_view: QDMGraphicsView instance
        """
        self.grScene = gr_view.grScene
        self.grView = gr_view
        self.draggedNode: Node | None = None
        self.hoveredList: list = []

    def enterState(self, node: Node) -> None:
        """Enter the node dragging state.

        Args:
            node: Node that started being dragged
        """
        self.hoveredList = []
        self.draggedNode = node

    def leaveState(self, scene_pos_x: float, scene_pos_y: float) -> None:
        """Leave the node dragging state.

        Args:
            scene_pos_x: Final X position in scene
            scene_pos_y: Final Y position in scene
        """
        self.dropNode(self.draggedNode, scene_pos_x, scene_pos_y)
        self.draggedNode = None
        self.hoveredList = []

    def dropNode(self, node: Node, scene_pos_x: float, scene_pos_y: float) -> None:
        """Handle dropping a node on an edge.

        Args:
            node: Node being dropped
            scene_pos_x: Drop X position
            scene_pos_y: Drop Y position
        """
        from node_editor.core.edge import Edge

        node_box = self.hotZoneRect(node)

        # Check if the node is dropped on an existing edge
        edge = self.intersect(node_box)
        if edge is None:
            return

        if self.isConnected(node):
            return

        # Determine the order of start and end
        if edge.start_socket.is_output:
            socket_start = edge.start_socket
            socket_end = edge.end_socket
        else:
            socket_start = edge.end_socket
            socket_end = edge.start_socket

        # The new edges will have the same edge_type as the intersected edge
        edge_type = edge.edge_type
        edge.remove()
        self.grView.grScene.scene.history.storeHistory('Delete existing edge', setModified=True)

        # Create new edges
        new_node_socket_in = node.inputs[0]
        Edge(self.grScene.scene, socket_start, new_node_socket_in, edge_type=edge_type)

        new_node_socket_out = node.outputs[0]
        Edge(self.grScene.scene, new_node_socket_out, socket_end, edge_type=edge_type)

        self.grView.grScene.scene.history.storeHistory('Created new edges by dropping node', setModified=True)

    def hotZoneRect(self, node: Node) -> QRectF:
        """Get a bounding rectangle around a node.

        Args:
            node: Node to get rectangle for

        Returns:
            QRectF describing node's position and area
        """
        node_pos = node.grNode.scenePos()
        x = node_pos.x()
        y = node_pos.y()
        w = node.grNode.width
        h = node.grNode.height
        return QRectF(x, y, w, h)

    def update(self, scene_pos_x: float, scene_pos_y: float) -> None:
        """Update during mouse move.

        Args:
            scene_pos_x: Current X position
            scene_pos_y: Current Y position
        """
        rect = self.hotZoneRect(self.draggedNode)
        gr_items = self.grScene.items(rect)

        # Reset hovered state
        for gr_edge in self.hoveredList:
            gr_edge.hovered = False
        self.hoveredList = []

        # Set new hovered items
        for gr_item in gr_items:
            if hasattr(gr_item, 'edge') and not self.draggedNode.hasConnectedEdge(gr_item.edge):
                self.hoveredList.append(gr_item)
                gr_item.hovered = True

    def intersect(self, node_box: QRectF) -> Edge | None:
        """Check for intersection with edges.

        Args:
            node_box: Rectangle to check for intersection

        Returns:
            First intersecting Edge or None
        """
        # Returns the first edge that intersects with the dropped node
        gr_items = self.grScene.items(node_box)
        for gr_item in gr_items:
            if hasattr(gr_item, 'edge') and not self.draggedNode.hasConnectedEdge(gr_item.edge):
                return gr_item.edge
        return None

    def isConnected(self, node: Node) -> bool:
        """Check if node has any connections.

        Args:
            node: Node to check

        Returns:
            True if node has connections
        """
        # Nodes with only inputs or outputs are excluded
        if node.inputs == [] or node.outputs == []:
            return True

        # Check if the node has edges connected
        return node.getInput() or node.getOutputs()
