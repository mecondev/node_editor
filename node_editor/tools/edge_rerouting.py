"""
Edge Rerouting - Interactive edge rerouting functionality.

This module handles the rerouting of existing edges by Ctrl+clicking on a socket
and dragging to a new destination.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from node_editor.core.edge import Edge
    from node_editor.core.socket import Socket
    from node_editor.graphics.view import QDMGraphicsView

DEBUG_REROUTING = False


class EdgeRerouting:
    """Handles edge rerouting interaction.

    Allows users to reroute existing edges by Ctrl+clicking on a socket
    that has connections and dragging to a new socket.

    Attributes:
        grView: Reference to the QDMGraphicsView
        start_socket: Socket where rerouting started
        rerouting_edges: Temporary dashed edges shown during rerouting
        is_rerouting: Flag indicating if currently rerouting
        first_mb_release: Flag for first mouse button release detection
    """

    def __init__(self, gr_view: QDMGraphicsView) -> None:
        """Initialize edge rerouting.

        Args:
            gr_view: QDMGraphicsView instance
        """
        self.grView = gr_view
        self.start_socket: Socket | None = None
        self.rerouting_edges: list[Edge] = []
        self.is_rerouting: bool = False
        self.first_mb_release: bool = False

    def print(self, *args) -> None:
        """Helper function for debug printing.

        Args:
            *args: Arguments to print
        """
        if DEBUG_REROUTING:
            pass

    def getEdgeClass(self) -> type[Edge]:
        """Get the Edge class to use.

        Returns:
            Edge class from the scene
        """
        return self.grView.grScene.scene.getEdgeClass()

    def getAffectedEdges(self) -> list[Edge]:
        """Get all edges connected to the start socket.

        Returns:
            List of edges affected by rerouting
        """
        if self.start_socket is None:
            return []
        return self.start_socket.edges.copy()

    def setAffectedEdgesVisible(self, visibility: bool = True) -> None:
        """Show or hide all affected edges.

        Args:
            visibility: True to show edges, False to hide them
        """
        for edge in self.getAffectedEdges():
            if visibility:
                edge.grEdge.show()
            else:
                edge.grEdge.hide()

    def resetRerouting(self) -> None:
        """Reset to default state."""
        self.is_rerouting = False
        self.start_socket = None
        self.first_mb_release = False

    def clearReroutingEdges(self) -> None:
        """Remove the helping dashed edges from the scene."""
        self.print("clean called")
        while self.rerouting_edges:
            edge = self.rerouting_edges.pop()
            self.print("\twant to clean:", edge)
            edge.remove()

    def updateScenePos(self, x: float, y: float) -> None:
        """Update position of all rerouting edges.

        Called from mouse move event to update to new mouse position.

        Args:
            x: New X position
            y: New Y position
        """
        if self.is_rerouting:
            for edge in self.rerouting_edges:
                if edge and edge.grEdge:
                    edge.grEdge.setDestination(x, y)
                    edge.grEdge.update()

    def startRerouting(self, socket: Socket) -> None:
        """Start the rerouting operation.

        Args:
            socket: Socket where rerouting started
        """
        self.print("startRerouting", socket)
        self.is_rerouting = True
        self.start_socket = socket

        self.print("numEdges:", len(self.getAffectedEdges()))
        self.setAffectedEdgesVisible(visibility=False)

        start_position = self.start_socket.node.getSocketScenePosition(self.start_socket)

        edge_class = self.getEdgeClass()
        for edge in self.getAffectedEdges():
            other_socket = edge.getOtherSocket(self.start_socket)

            new_edge = edge_class(self.start_socket.node.scene, edge_type=edge.edge_type)
            new_edge.start_socket = other_socket
            new_edge.grEdge.setSource(*other_socket.node.getSocketScenePosition(other_socket))
            new_edge.grEdge.setDestination(*start_position)
            new_edge.grEdge.update()
            self.rerouting_edges.append(new_edge)

    def stopRerouting(self, target: Socket | None = None) -> None:
        """Stop the rerouting operation.

        Args:
            target: Target socket where rerouting ended (None to cancel)
        """
        self.print("stopRerouting on:", target, "no change" if target == self.start_socket else "")

        if self.start_socket is not None:
            # Reset start socket highlight
            self.start_socket.grSocket.isHighlighted = False

        # Collect all affected (node, edge) tuples
        affected_nodes = []

        if target is None or target == self.start_socket:
            # Canceling - no change
            self.setAffectedEdgesVisible(visibility=True)
        else:
            # Validate edges before doing anything
            valid_edges = self.getAffectedEdges()
            invalid_edges = []

            for edge in self.getAffectedEdges():
                start_sock = edge.getOtherSocket(self.start_socket)
                if not edge.validateEdge(start_sock, target):
                    # Not valid edge
                    self.print("This edge rerouting is not valid!", edge)
                    invalid_edges.append(edge)

            # Remove the invalidated edges from the list
            for invalid_edge in invalid_edges:
                valid_edges.remove(invalid_edge)

            # Reconnect to new socket
            self.print("should reconnect from:", self.start_socket, "-->", target)

            self.setAffectedEdgesVisible(visibility=True)

            for edge in valid_edges:
                for node in [edge.start_socket.node, edge.end_socket.node]:
                    if node not in [n for n, e in affected_nodes]:
                        affected_nodes.append((node, edge))

                if target.is_input:
                    target.removeAllEdges(silent=True)

                if edge.end_socket == self.start_socket:
                    edge.end_socket = target
                else:
                    edge.start_socket = target

                edge.updatePositions()

        # Hide rerouting edges
        self.clearReroutingEdges()

        # Send notifications for all affected nodes
        for affected_node, edge in affected_nodes:
            affected_node.onEdgeConnectionChanged(edge)
            if edge.start_socket in affected_node.inputs:
                affected_node.onInputChanged(edge.start_socket)
            if edge.end_socket in affected_node.inputs:
                affected_node.onInputChanged(edge.end_socket)

        # Store history stamp
        if self.start_socket:
            self.start_socket.node.scene.history.storeHistory("Rerouted edges", setModified=True)

        # Reset variables
        self.resetRerouting()
