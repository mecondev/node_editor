"""Interactive edge creation by dragging from sockets.

This module provides EdgeDragging, which manages the interactive creation
of edges by clicking on a socket and dragging to another socket.

The dragging workflow:
    1. User clicks on a socket
    2. Temporary edge follows mouse cursor
    3. User releases on target socket
    4. If valid, permanent edge is created

Author:
    Michael Economou

Date:
    2025-12-11
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from node_editor.core.edge import EDGE_TYPE_DEFAULT
from node_editor.utils.helpers import dump_exception

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QGraphicsItem

    from node_editor.core.edge import Edge
    from node_editor.graphics.socket import QDMGraphicsSocket
    from node_editor.graphics.view import QDMGraphicsView


class EdgeDragging:
    """Manages edge creation through click-and-drag interaction.

    Creates temporary edge that follows cursor during drag, then
    validates and creates permanent edge on release.

    Attributes:
        grView: QDMGraphicsView for coordinate mapping.
        drag_edge: Temporary Edge shown during drag.
        drag_start_socket: Socket where drag originated.
    """

    def __init__(self, gr_view: QDMGraphicsView) -> None:
        """Initialize edge dragging helper.

        Args:
            gr_view: QDMGraphicsView to operate on.
        """
        self.grView = gr_view
        self.drag_edge: Edge | None = None
        self.drag_start_socket = None

    def getEdgeClass(self) -> type[Edge]:
        """Get Edge class configured for this scene.

        Returns:
            Edge class type for creating new edges.
        """
        return self.grView.grScene.scene.getEdgeClass()

    def updateDestination(self, x: float, y: float) -> None:
        """Move drag edge endpoint to new position.

        Args:
            x: Scene X coordinate.
            y: Scene Y coordinate.
        """
        if self.drag_edge is not None and self.drag_edge.grEdge is not None:
            self.drag_edge.grEdge.setDestination(x, y)
            self.drag_edge.grEdge.update()

    def edgeDragStart(self, item: QDMGraphicsSocket) -> None:
        """Begin edge drag from a socket.

        Creates temporary dashed edge starting from clicked socket.

        Args:
            item: QDMGraphicsSocket where drag started.
        """
        try:
            self.drag_start_socket = item.socket
            edge_class = self.getEdgeClass()
            self.drag_edge = edge_class(
                item.socket.node.scene,
                item.socket,
                None,
                EDGE_TYPE_DEFAULT
            )
            self.drag_edge.grEdge.makeUnselectable()

        except Exception as e:
            dump_exception(e)

    def edgeDragEnd(self, item: QGraphicsItem | None) -> bool:
        """Complete edge drag and create permanent edge if valid.

        Validates the connection and creates a permanent edge if
        the target is a valid socket. Handles edge removal for
        single-connection sockets.

        Args:
            item: Target graphics item, or None to cancel.

        Returns:
            True if edge was created, False otherwise.
        """
        from node_editor.graphics.socket import QDMGraphicsSocket

        if not isinstance(item, QDMGraphicsSocket):
            self.grView.resetMode()
            if self.drag_edge:
                self.drag_edge.remove(silent=True)
            self.drag_edge = None
            return False

        if isinstance(item, QDMGraphicsSocket):
            if not self.drag_edge.validateEdge(self.drag_start_socket, item.socket):
                return False

            self.grView.resetMode()

            if self.drag_edge:
                self.drag_edge.remove(silent=True)
            self.drag_edge = None

            try:
                if item.socket != self.drag_start_socket:
                    for socket in (item.socket, self.drag_start_socket):
                        if not socket.is_multi_edges:
                            if socket.is_input:
                                socket.removeAllEdges(silent=True)
                            else:
                                socket.removeAllEdges(silent=False)

                    edge_class = self.getEdgeClass()
                    new_edge = edge_class(
                        item.socket.node.scene,
                        self.drag_start_socket,
                        item.socket,
                        edge_type=EDGE_TYPE_DEFAULT
                    )

                    for socket in [self.drag_start_socket, item.socket]:
                        socket.node.onEdgeConnectionChanged(new_edge)
                        if socket.is_input:
                            socket.node.onInputChanged(socket)

                    self.grView.grScene.scene.history.storeHistory(
                        "Created new edge by dragging", set_modified=True
                    )
                    return True

            except Exception as e:
                dump_exception(e)

        return False
