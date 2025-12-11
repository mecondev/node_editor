"""Socket connection points for node inputs and outputs.

This module defines the Socket class representing connection endpoints on nodes.
Sockets serve as anchors for edges, enabling visual connections between nodes
in the graph. Each socket has a type (affecting visual appearance and
connection compatibility) and can be configured for single or multiple
simultaneous connections.

Position Constants:
    LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM: Input socket positions.
    RIGHT_TOP, RIGHT_CENTER, RIGHT_BOTTOM: Output socket positions.

Author:
    Michael Economou

Date:
    2025-12-11
"""

from collections import OrderedDict
from typing import TYPE_CHECKING

from node_editor.core.serializable import Serializable

if TYPE_CHECKING:
    from node_editor.core.edge import Edge
    from node_editor.core.node import Node
    from node_editor.graphics.socket import QDMGraphicsSocket

# Socket position constants for node layout
LEFT_TOP = 1
LEFT_CENTER = 2
LEFT_BOTTOM = 3
RIGHT_TOP = 4
RIGHT_CENTER = 5
RIGHT_BOTTOM = 6

DEBUG_REMOVE_WARNINGS = False


class Socket(Serializable):
    """Connection point on a node for attaching edges.

    Sockets are the interface between nodes and edges. Input sockets receive
    data from connected output sockets, while output sockets send data out.
    Each socket maintains a list of connected edges and manages connection
    lifecycle (add/remove edges).

    The socket type determines visual appearance (color) and can be used for
    type-checking connections. Multi-edge sockets allow multiple simultaneous
    connections; single-edge sockets disconnect existing edges when a new
    connection is made.

    Attributes:
        node: Parent node that owns this socket.
        index: Zero-based index among sockets on the same side.
        position: Position constant (LEFT_TOP, RIGHT_CENTER, etc.).
        socket_type: Integer type identifier affecting visual color.
        is_multi_edges: True if multiple edges can connect simultaneously.
        is_input: True for input sockets (left side).
        is_output: True for output sockets (right side).
        edges: List of currently connected Edge instances.
        grSocket: Associated QDMGraphicsSocket for visual representation.
        count_on_this_node_side: Total socket count on this side for layout.

    Class Attributes:
        Socket_GR_Class: Graphics class for socket visualization (set at init).
    """

    Socket_GR_Class: type["QDMGraphicsSocket"] | None = None

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
        """Create a socket attached to a node.

        Args:
            node: Parent node that will contain this socket.
            index: Socket index on this side of the node (0-based).
            position: Position constant determining socket placement.
            socket_type: Type identifier for visual styling and compatibility.
            multi_edges: Allow multiple simultaneous edge connections.
            count_on_this_node_side: Total sockets on this side for layout calc.
            is_input: True for input socket, False for output socket.
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

        self.grSocket: QDMGraphicsSocket = self.__class__.Socket_GR_Class(self)
        self.setSocketPosition()

        self.edges: list[Edge] = []

    def __str__(self) -> str:
        """Return human-readable socket representation.

        Returns:
            Format: <Socket #index ME|SE ID> where ME=multi-edge, SE=single-edge.
        """
        edge_type = "ME" if self.is_multi_edges else "SE"
        return f"<Socket #{self.index} {edge_type} {hex(id(self))[2:5]}..{hex(id(self))[-3:]}>"

    def delete(self) -> None:
        """Remove socket from scene and clean up graphics resources.

        Detaches the graphics socket from its parent and removes it from
        the graphics scene. Should be called before discarding the socket.
        """
        self.grSocket.setParentItem(None)
        self.node.scene.grScene.removeItem(self.grSocket)
        del self.grSocket

    def changeSocketType(self, new_socket_type: int) -> bool:
        """Update socket type and refresh visual appearance.

        Args:
            new_socket_type: New type identifier for the socket.

        Returns:
            True if type changed, False if already set to this type.
        """
        if self.socket_type != new_socket_type:
            self.socket_type = new_socket_type
            self.grSocket.changeSocketType()
            return True
        return False

    def setSocketPosition(self) -> None:
        """Update graphics socket position based on current node layout.

        Queries the parent node for this socket's position and updates
        the graphics socket accordingly.
        """
        pos = self.node.getSocketPosition(
            self.index, self.position, self.count_on_this_node_side
        )
        self.grSocket.setPos(*pos)

    def getSocketPosition(self) -> tuple[float, float]:
        """Calculate socket position in node-local coordinates.

        Returns:
            Tuple of (x, y) position relative to parent node.
        """
        result = self.node.getSocketPosition(
            self.index, self.position, self.count_on_this_node_side
        )
        return result

    def hasAnyEdge(self) -> bool:
        """Check if socket has any connected edges.

        Returns:
            True if at least one edge is connected to this socket.
        """
        return len(self.edges) > 0

    def isConnected(self, edge: "Edge") -> bool:
        """Check if a specific edge is connected to this socket.

        Args:
            edge: Edge instance to check for connection.

        Returns:
            True if the edge is in this socket's edge list.
        """
        return edge in self.edges

    def addEdge(self, edge: "Edge") -> None:
        """Register an edge as connected to this socket.

        Args:
            edge: Edge to add to the connection list.
        """
        self.edges.append(edge)

    def removeEdge(self, edge: "Edge") -> None:
        """Unregister an edge from this socket.

        Args:
            edge: Edge to remove from the connection list.

        Note:
            Silently ignores if edge is not connected.
        """
        if edge in self.edges:
            self.edges.remove(edge)
        elif DEBUG_REMOVE_WARNINGS:
            pass

    def removeAllEdges(self, silent: bool = False) -> None:
        """Disconnect and remove all edges from this socket.

        Iterates through all connected edges and removes them. Each edge
        is properly cleaned up through its remove() method.

        Args:
            silent: If True, suppress removal notifications to this socket.
        """
        while self.edges:
            edge = self.edges.pop(0)
            if silent:
                edge.remove(silent_for_socket=self)
            else:
                edge.remove()

    def determineMultiEdges(self, data: dict) -> bool:
        """Determine multi-edge capability from serialized data.

        Handles backward compatibility with older file formats that didn't
        explicitly store multi_edges flag.

        Args:
            data: Deserialized socket data dictionary.

        Returns:
            True if socket should allow multiple edge connections.
        """
        if "multi_edges" in data:
            return data["multi_edges"]
        # Legacy format: output sockets (RIGHT_*) were multi-edge by default
        return data["position"] in (RIGHT_BOTTOM, RIGHT_TOP)

    def serialize(self) -> OrderedDict:
        """Convert socket state to ordered dictionary for persistence.

        Returns:
            OrderedDict containing socket configuration and ID.
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
        """Restore socket state from serialized dictionary.

        Args:
            data: Dictionary containing serialized socket data.
            hashmap: Maps original IDs to restored objects for references.
            restore_id: If True, restore original ID from data.

        Returns:
            True on successful deserialization.
        """
        if hashmap is None:
            hashmap = {}

        if restore_id:
            self.id = data["id"]
        self.is_multi_edges = self.determineMultiEdges(data)
        self.changeSocketType(data["socket_type"])
        hashmap[data["id"]] = self
        return True

