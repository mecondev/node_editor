"""
Socket class for node connection points.

Author: Michael Economou
Date: 2025-12-11
"""

from collections import OrderedDict
from typing import TYPE_CHECKING

from node_editor.core.serializable import Serializable

if TYPE_CHECKING:
    from node_editor.core.edge import Edge
    from node_editor.core.node import Node
    from node_editor.graphics.socket import QDMGraphicsSocket

# Socket position constants
LEFT_TOP = 1
LEFT_CENTER = 2
LEFT_BOTTOM = 3
RIGHT_TOP = 4
RIGHT_CENTER = 5
RIGHT_BOTTOM = 6

DEBUG = False
DEBUG_REMOVE_WARNINGS = False


class Socket(Serializable):
    """Socket for connecting nodes with edges.

    Represents a connection point on a node. Can be input or output,
    and can support single or multiple edge connections.

    Attributes:
        node: Parent node containing this socket
        index: Socket index on its side of the node
        position: Socket position (LEFT_TOP, RIGHT_CENTER, etc.)
        socket_type: Type/color identifier for the socket
        is_multi_edges: Whether multiple edges can connect
        is_input: True if input socket, False if output
        is_output: True if output socket, False if input
        edges: List of connected edges
        grSocket: Graphics representation
    """

    Socket_GR_Class: type["QDMGraphicsSocket"] | None = None  # Set at module load

    def __init__(
        self,
        node: "Node",
        index: int = 0,
        position: int = LEFT_TOP,
        socket_type: int = 1,
        multi_edges: bool = True,
        count_on_this_node_side: int = 1,
        is_input: bool = False
    ):
        """Initialize socket.

        Args:
            node: Parent node
            index: Socket index on this side
            position: Socket position constant
            socket_type: Type identifier (affects color)
            multi_edges: Allow multiple edge connections
            count_on_this_node_side: Total sockets on this side
            is_input: True for input socket
        """
        super().__init__()

        self.node = node
        self.position = position
        self.index = index
        self.socket_type = socket_type
        self.count_on_this_node_side = count_on_this_node_side
        self.is_multi_edges = multi_edges
        self.is_input = is_input
        self.is_output = not self.is_input

        if DEBUG:
            pass

        # Create graphics socket
        self.grSocket: QDMGraphicsSocket = self.__class__.Socket_GR_Class(self)
        self.setSocketPosition()

        self.edges: list[Edge] = []

    def __str__(self) -> str:
        edge_type = "ME" if self.is_multi_edges else "SE"
        return f"<Socket #{self.index} {edge_type} {hex(id(self))[2:5]}..{hex(id(self))[-3:]}>"

    def delete(self) -> None:
        """Delete socket and remove from graphics scene."""
        self.grSocket.setParentItem(None)
        self.node.scene.grScene.removeItem(self.grSocket)
        del self.grSocket

    def changeSocketType(self, new_socket_type: int) -> bool:
        """Change socket type/color.

        Args:
            new_socket_type: New type identifier

        Returns:
            True if type was changed
        """
        if self.socket_type != new_socket_type:
            self.socket_type = new_socket_type
            self.grSocket.changeSocketType()
            return True
        return False

    def setSocketPosition(self) -> None:
        """Update graphics socket position based on node layout."""
        pos = self.node.getSocketPosition(
            self.index, self.position, self.count_on_this_node_side
        )
        self.grSocket.setPos(*pos)

    def getSocketPosition(self) -> tuple[float, float]:
        """Get socket position from node.

        Returns:
            (x, y) position tuple
        """
        if DEBUG:
            pass
        result = self.node.getSocketPosition(
            self.index, self.position, self.count_on_this_node_side
        )
        if DEBUG:
            pass
        return result

    def hasAnyEdge(self) -> bool:
        """Check if any edge is connected.

        Returns:
            True if at least one edge is connected
        """
        return len(self.edges) > 0

    def isConnected(self, edge: "Edge") -> bool:
        """Check if specific edge is connected.

        Args:
            edge: Edge to check

        Returns:
            True if edge is connected to this socket
        """
        return edge in self.edges

    def addEdge(self, edge: "Edge") -> None:
        """Add edge to connected edges list.

        Args:
            edge: Edge to add
        """
        self.edges.append(edge)

    def removeEdge(self, edge: "Edge") -> None:
        """Remove edge from connected edges list.

        Args:
            edge: Edge to remove
        """
        if edge in self.edges:
            self.edges.remove(edge)
        elif DEBUG_REMOVE_WARNINGS:
            pass

    def removeAllEdges(self, silent: bool = False) -> None:
        """Disconnect all edges from this socket.

        Args:
            silent: If True, don't notify about removals
        """
        while self.edges:
            edge = self.edges.pop(0)
            if silent:
                edge.remove(silent_for_socket=self)
            else:
                edge.remove()

    def determineMultiEdges(self, data: dict) -> bool:
        """Determine if socket should support multi-edges (for old file format).

        Args:
            data: Deserialized socket data

        Returns:
            True if socket should support multiple edges
        """
        if "multi_edges" in data:
            return data["multi_edges"]
        # Older format: RIGHT sockets were multi-edge by default
        return data["position"] in (RIGHT_BOTTOM, RIGHT_TOP)

    def serialize(self) -> OrderedDict:
        """Serialize socket to dictionary.

        Returns:
            OrderedDict with socket data
        """
        return OrderedDict([
            ("id", self.id),
            ("index", self.index),
            ("multi_edges", self.is_multi_edges),
            ("position", self.position),
            ("socket_type", self.socket_type),
        ])

    def deserialize(
        self,
        data: dict,
        hashmap: dict | None = None,
        restore_id: bool = True
    ) -> bool:
        """Deserialize socket from dictionary.

        Args:
            data: Dictionary with socket data
            hashmap: Map of IDs to objects
            restore_id: Whether to restore the ID

        Returns:
            True if successful
        """
        if hashmap is None:
            hashmap = {}

        if restore_id:
            self.id = data["id"]
        self.is_multi_edges = self.determineMultiEdges(data)
        self.changeSocketType(data["socket_type"])
        hashmap[data["id"]] = self
        return True

