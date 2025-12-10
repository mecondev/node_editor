"""
Edge Dragging - Interactive edge creation by dragging.

This module handles the interactive creation of edges by dragging from
one socket to another.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from node_editor.core.edge import EDGE_TYPE_DEFAULT
from node_editor.utils.helpers import dump_exception

if TYPE_CHECKING:
    from node_editor.graphics.view import QDMGraphicsView
    from node_editor.graphics.socket import QDMGraphicsSocket
    from node_editor.core.edge import Edge
    from PyQt5.QtWidgets import QGraphicsItem

DEBUG = False


class EdgeDragging:
    """Handles edge dragging interaction for creating new edges.
    
    When a user clicks on a socket and drags, this class manages the temporary
    edge that follows the mouse until the user releases on another socket.
    
    Attributes:
        grView: Reference to the QDMGraphicsView
        drag_edge: Temporary edge being dragged
        drag_start_socket: Socket where the drag started
    """
    
    def __init__(self, grView: QDMGraphicsView) -> None:
        """Initialize edge dragging.
        
        Args:
            grView: QDMGraphicsView instance
        """
        self.grView = grView
        self.drag_edge: Edge | None = None
        self.drag_start_socket = None
    
    def getEdgeClass(self) -> type[Edge]:
        """Get the Edge class to use for creating edges.
        
        Returns:
            Edge class from the scene
        """
        return self.grView.grScene.scene.getEdgeClass()
    
    def updateDestination(self, x: float, y: float) -> None:
        """Update the end point of the dragging edge.
        
        Args:
            x: New X scene position
            y: New Y scene position
        """
        if self.drag_edge is not None and self.drag_edge.grEdge is not None:
            self.drag_edge.grEdge.setDestination(x, y)
            self.drag_edge.grEdge.update()
        else:
            if DEBUG:
                print(">>> Want to update self.drag_edge grEdge, but it's None!!!")
    
    def edgeDragStart(self, item: QDMGraphicsSocket) -> None:
        """Start dragging an edge from a socket.
        
        Args:
            item: Socket graphics item where dragging started
        """
        try:
            if DEBUG:
                print('View::edgeDragStart ~ Start dragging edge')
                print('View::edgeDragStart ~   assign Start Socket to:', item.socket)
            
            self.drag_start_socket = item.socket
            EdgeClass = self.getEdgeClass()
            self.drag_edge = EdgeClass(
                item.socket.node.scene,
                item.socket,
                None,
                EDGE_TYPE_DEFAULT
            )
            self.drag_edge.grEdge.makeUnselectable()
            
            if DEBUG:
                print('View::edgeDragStart ~   dragEdge:', self.drag_edge)
        
        except Exception as e:
            dump_exception(e)
    
    def edgeDragEnd(self, item: QGraphicsItem | None) -> bool:
        """End dragging an edge.
        
        This method handles the logic for completing or canceling an edge drag.
        If the user releases on a valid socket, a new edge is created.
        
        Args:
            item: Graphics item where the drag ended (can be None to cancel)
            
        Returns:
            True if the event was handled and should not propagate
        """
        from node_editor.graphics.socket import QDMGraphicsSocket
        
        # Early out - clicked on something other than a socket
        if not isinstance(item, QDMGraphicsSocket):
            self.grView.resetMode()
            if DEBUG:
                print('View::edgeDragEnd ~ End dragging edge early')
            if self.drag_edge:
                self.drag_edge.remove(silent=True)  # Don't notify sockets
            self.drag_edge = None
            return False
        
        # Clicked on a socket
        if isinstance(item, QDMGraphicsSocket):
            # Check if edge would be valid
            if not self.drag_edge.validateEdge(self.drag_start_socket, item.socket):
                if DEBUG:
                    print("NOT VALID EDGE")
                return False
            
            # Regular processing of drag edge
            self.grView.resetMode()
            
            if DEBUG:
                print('View::edgeDragEnd ~ End dragging edge')
            
            if self.drag_edge:
                self.drag_edge.remove(silent=True)  # Don't notify sockets
            self.drag_edge = None
            
            try:
                if item.socket != self.drag_start_socket:
                    # Released on a different socket
                    
                    # First remove old edges / send notifications
                    for socket in (item.socket, self.drag_start_socket):
                        if not socket.is_multi_edges:
                            if socket.is_input:
                                # Remove existing edges from input socket
                                socket.removeAllEdges(silent=True)
                            else:
                                socket.removeAllEdges(silent=False)
                    
                    # Create new edge
                    EdgeClass = self.getEdgeClass()
                    new_edge = EdgeClass(
                        item.socket.node.scene,
                        self.drag_start_socket,
                        item.socket,
                        edge_type=EDGE_TYPE_DEFAULT
                    )
                    
                    if DEBUG:
                        print(
                            "View::edgeDragEnd ~  created new edge:", new_edge,
                            "connecting", new_edge.start_socket, "<-->", new_edge.end_socket
                        )
                    
                    # Send notifications for the new edge
                    for socket in [self.drag_start_socket, item.socket]:
                        socket.node.onEdgeConnectionChanged(new_edge)
                        if socket.is_input:
                            socket.node.onInputChanged(socket)
                    
                    self.grView.grScene.scene.history.storeHistory(
                        "Created new edge by dragging", setModified=True
                    )
                    return True
            
            except Exception as e:
                dump_exception(e)
        
        if DEBUG:
            print('View::edgeDragEnd ~ everything done.')
        
        return False
