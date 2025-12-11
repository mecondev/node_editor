"""
Edge Snapping - Socket snapping functionality.

This module provides socket snapping to help users connect edges more easily
by automatically snapping to nearby sockets.

Author: Michael Economou
Date: 2025-12-11
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt5.QtCore import QPointF, QRectF

if TYPE_CHECKING:
    from PyQt5.QtGui import QMouseEvent

    from node_editor.graphics.socket import QDMGraphicsSocket
    from node_editor.graphics.view import QDMGraphicsView


class EdgeSnapping:
    """Handles socket snapping for easier edge connections.

    When dragging an edge, this class helps snap the end point to nearby
    sockets within a specified radius.

    Attributes:
        grView: Reference to the QDMGraphicsView
        grScene: Reference to the QDMGraphicsScene
        edge_snapping_radius: Radius within which to snap to sockets
    """

    def __init__(self, gr_view: QDMGraphicsView, snapping_radius: float = 24) -> None:
        """Initialize edge snapping.

        Args:
            gr_view: QDMGraphicsView instance
            snapping_radius: Radius for socket snapping
        """
        self.grView = gr_view
        self.grScene = self.grView.grScene
        self.edge_snapping_radius = snapping_radius

    def getSnappedSocketItem(self, event: QMouseEvent) -> QDMGraphicsSocket | None:
        """Get the socket item to snap to based on mouse event.

        Args:
            event: Mouse event

        Returns:
            QDMGraphicsSocket to snap to or None
        """
        scenepos = self.grView.mapToScene(event.pos())
        gr_socket, pos = self.getSnappedToSocketPosition(scenepos)
        return gr_socket

    def getSnappedToSocketPosition(
        self, scenepos: QPointF
    ) -> tuple[QDMGraphicsSocket | None, QPointF]:
        """Get socket and position to snap to.

        Args:
            scenepos: Current scene position

        Returns:
            Tuple of (socket to snap to or None, snapped position)
        """
        from node_editor.graphics.socket import QDMGraphicsSocket

        scanrect = QRectF(
            scenepos.x() - self.edge_snapping_radius,
            scenepos.y() - self.edge_snapping_radius,
            self.edge_snapping_radius * 2,
            self.edge_snapping_radius * 2
        )
        items = self.grScene.items(scanrect)
        items = list(filter(lambda x: isinstance(x, QDMGraphicsSocket), items))

        if len(items) == 0:
            return None, scenepos

        selected_item = items[0]
        if len(items) > 1:
            # Calculate the nearest socket
            nearest = float('inf')
            for grsock in items:
                grsock_scenepos = grsock.socket.node.getSocketScenePosition(grsock.socket)
                qpdist = QPointF(*grsock_scenepos) - scenepos
                dist = qpdist.x() * qpdist.x() + qpdist.y() * qpdist.y()
                if dist < nearest:
                    nearest = dist
                    selected_item = grsock

        selected_item.isHighlighted = True

        calcpos = selected_item.socket.node.getSocketScenePosition(selected_item.socket)

        return selected_item, QPointF(*calcpos)
