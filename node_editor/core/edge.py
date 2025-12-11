"""
Edge class for connecting nodes and edge type constants.

Author: Michael Economou
Date: 2025-12-11
"""

import contextlib
from collections import OrderedDict
from typing import TYPE_CHECKING

from node_editor.core.serializable import Serializable
from node_editor.utils.helpers import dumpException

if TYPE_CHECKING:
    from node_editor.core.scene import Scene
    from node_editor.core.socket import Socket
    from node_editor.graphics.edge import QDMGraphicsEdge

# Edge type constants
EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2
EDGE_TYPE_SQUARE = 3
EDGE_TYPE_IMPROVED_SHARP = 4
EDGE_TYPE_IMPROVED_BEZIER = 5
EDGE_TYPE_DEFAULT = EDGE_TYPE_IMPROVED_BEZIER

DEBUG = False


class Edge(Serializable):
    """Class for representing edge in node editor.

    An edge connects two sockets (start and end) and has a visual
    representation determined by edge_type.

    Attributes:
        scene: Reference to parent Scene
        start_socket: Starting socket
        end_socket: Ending socket or None if dragging
        edge_type: Type constant determining visual style
        grEdge: Graphics representation (QDMGraphicsEdge)
    """

    edge_validators: list = []  # Class variable for edge validators
    GraphicsEdge_class: type["QDMGraphicsEdge"] | None = None  # Set at module load

    def __init__(
        self,
        scene: "Scene",
        start_socket: "Socket | None" = None,
        end_socket: "Socket | None" = None,
        edge_type: int = EDGE_TYPE_DEFAULT,
    ):
        """Initialize edge.

        Args:
            scene: Reference to parent Scene
            start_socket: Reference to starting socket
            end_socket: Reference to end socket or None
            edge_type: Constant determining edge type
        """
        super().__init__()
        self.scene = scene

        # Initialize sockets
        self._start_socket: Socket | None = None
        self._end_socket: Socket | None = None

        self.start_socket = start_socket
        self.end_socket = end_socket
        self._edge_type = edge_type

        # Create graphics edge instance
        self.grEdge = self.createEdgeClassInstance()

        self.scene.addEdge(self)

    def __str__(self) -> str:
        return (
            f"<Edge {hex(id(self))[2:5]}..{hex(id(self))[-3:]} -- "
            f"S:{self.start_socket} E:{self.end_socket}>"
        )

    @property
    def start_socket(self) -> "Socket | None":
        """Start socket.

        Returns:
            Start socket or None
        """
        return self._start_socket

    @start_socket.setter
    def start_socket(self, value: "Socket | None") -> None:
        """Set start socket safely.

        Args:
            value: New start socket
        """
        # Remove from previous socket
        if self._start_socket is not None:
            self._start_socket.removeEdge(self)

        # Assign new start socket
        self._start_socket = value
        if self.start_socket is not None:
            self.start_socket.addEdge(self)

    @property
    def end_socket(self) -> "Socket | None":
        """End socket.

        Returns:
            End socket or None if not connected
        """
        return self._end_socket

    @end_socket.setter
    def end_socket(self, value: "Socket | None") -> None:
        """Set end socket safely.

        Args:
            value: New end socket
        """
        # Remove from previous socket
        if self._end_socket is not None:
            self._end_socket.removeEdge(self)

        # Assign new end socket
        self._end_socket = value
        if self.end_socket is not None:
            self.end_socket.addEdge(self)

    @property
    def edge_type(self) -> int:
        """Edge type constant.

        Returns:
            Edge type constant
        """
        return self._edge_type

    @edge_type.setter
    def edge_type(self, value: int) -> None:
        """Set edge type and update graphics.

        Args:
            value: New edge type constant
        """
        self._edge_type = value

        # Update graphics edge path calculator
        self.grEdge.createEdgePathCalculator()

        if self.start_socket is not None:
            self.updatePositions()

    @classmethod
    def getEdgeValidators(cls) -> list:
        """Get list of edge validator callbacks.

        Returns:
            List of validator functions
        """
        return cls.edge_validators

    @classmethod
    def registerEdgeValidator(cls, validator_callback) -> None:
        """Register edge validator callback.

        Args:
            validator_callback: Function to validate edge
        """
        cls.edge_validators.append(validator_callback)

    @classmethod
    def validateEdge(cls, start_socket: "Socket", end_socket: "Socket") -> bool:
        """Validate edge against all registered validators.

        Args:
            start_socket: Starting socket to check
            end_socket: Target/end socket to check

        Returns:
            True if edge is valid
        """
        return all(validator(start_socket, end_socket) for validator in cls.getEdgeValidators())

    def reconnect(self, from_socket: "Socket", to_socket: "Socket") -> None:
        """Reconnect edge from one socket to another.

        Args:
            from_socket: Socket to disconnect from
            to_socket: Socket to connect to
        """
        if self.start_socket == from_socket:
            self.start_socket = to_socket
        elif self.end_socket == from_socket:
            self.end_socket = to_socket

    def getGraphicsEdgeClass(self) -> type["QDMGraphicsEdge"]:
        """Get class representing graphics edge.

        Returns:
            Graphics edge class
        """
        return self.__class__.GraphicsEdge_class

    def createEdgeClassInstance(self) -> "QDMGraphicsEdge":
        """Create instance of graphics edge.

        Returns:
            Instance of graphics edge
        """
        self.grEdge = self.getGraphicsEdgeClass()(self)
        self.scene.grScene.addItem(self.grEdge)
        if self.start_socket is not None:
            self.updatePositions()
        return self.grEdge

    def getOtherSocket(self, known_socket: "Socket") -> "Socket | None":
        """Get opposite socket on this edge.

        Args:
            known_socket: Known socket to determine opposite

        Returns:
            Opposite socket or None
        """
        return self.start_socket if known_socket == self.end_socket else self.end_socket

    def doSelect(self, new_state: bool = True) -> None:
        """Safe selecting/deselecting operation.

        Args:
            new_state: True to select, False to deselect
        """
        self.grEdge.doSelect(new_state)

    def updatePositions(self) -> None:
        """Update graphics edge positions from sockets."""
        source_pos = list(self.start_socket.getSocketPosition())
        source_pos[0] += self.start_socket.node.grNode.pos().x()
        source_pos[1] += self.start_socket.node.grNode.pos().y()
        self.grEdge.setSource(*source_pos)

        if self.end_socket is not None:
            end_pos = list(self.end_socket.getSocketPosition())
            end_pos[0] += self.end_socket.node.grNode.pos().x()
            end_pos[1] += self.end_socket.node.grNode.pos().y()
            self.grEdge.setDestination(*end_pos)
        else:
            self.grEdge.setDestination(*source_pos)

        self.grEdge.update()

    def remove_from_sockets(self) -> None:
        """Remove edge from both sockets."""
        self.end_socket = None
        self.start_socket = None

    def remove(self, silent_for_socket: "Socket | None" = None, silent: bool = False) -> None:
        """Safely remove this edge.

        Removes graphics edge and notifies connected nodes.

        Args:
            silent_for_socket: Socket that won't be notified
            silent: True if no events should be triggered
        """
        old_sockets = [self.start_socket, self.end_socket]

        # Hide graphics edge
        if DEBUG:
            pass
        self.grEdge.hide()

        if DEBUG:
            pass
        self.scene.grScene.removeItem(self.grEdge)

        self.scene.grScene.update()

        if DEBUG:
            pass
        if DEBUG:
            pass
        self.remove_from_sockets()

        if DEBUG:
            pass
        with contextlib.suppress(ValueError):
            self.scene.removeEdge(self)

        if DEBUG:
            pass

        try:
            # Notify nodes from old sockets
            for socket in old_sockets:
                if socket and socket.node:
                    if silent:
                        continue
                    if silent_for_socket is not None and socket == silent_for_socket:
                        # Skip notifications for requested socket
                        continue

                    # Notify socket's node
                    socket.node.onEdgeConnectionChanged(self)
                    if socket.is_input:
                        socket.node.onInputChanged(socket)

        except Exception as e:
            dumpException(e)

    def serialize(self) -> OrderedDict:
        """Serialize edge to dictionary.

        Returns:
            OrderedDict with edge data
        """
        return OrderedDict(
            [
                ("id", self.id),
                ("edge_type", self.edge_type),
                (
                    "start",
                    self.start_socket.id if self.start_socket is not None else None,
                ),
                ("end", self.end_socket.id if self.end_socket is not None else None),
            ]
        )

    def deserialize(
        self,
        data: dict,
        hashmap: dict | None = None,
        restore_id: bool = True,
        *_args,
        **_kwargs,
    ) -> bool:
        """Deserialize edge from dictionary.

        Args:
            data: Dictionary with edge data
            hashmap: Map of IDs to objects
            restore_id: Whether to restore the ID

        Returns:
            True if successful
        """
        if hashmap is None:
            hashmap = {}

        if restore_id:
            self.id = data["id"]
        self.start_socket = hashmap[data["start"]]
        self.end_socket = hashmap[data["end"]]
        self.edge_type = data["edge_type"]
        return True
