"""
Node class - logical representation of a node.

Author: Michael Economou
Date: 2025-12-11
"""

from collections import OrderedDict
from typing import TYPE_CHECKING

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
from node_editor.utils.helpers import dumpException

if TYPE_CHECKING:
    from PyQt5.QtCore import QPointF

    from node_editor.core.edge import Edge
    from node_editor.core.scene import Scene
    from node_editor.graphics.node import QDMGraphicsNode
    from node_editor.widgets.content_widget import QDMNodeContentWidget

DEBUG = False


class Node(Serializable):
    """Class representing Node in the Scene.

    A node contains sockets for connections, content widget for UI,
    and graphics representation for visualization.

    Attributes:
        scene: Reference to parent Scene
        title: Node title displayed in graphics
        grNode: Graphics representation (QDMGraphicsNode)
        content: Content widget (QDMNodeContentWidget)
        inputs: List of input sockets
        outputs: List of output sockets
    """

    GraphicsNode_class: type["QDMGraphicsNode"] | None = None  # Set at module load
    NodeContent_class: type["QDMNodeContentWidget"] | None = None  # Set at module load
    Socket_class = Socket

    def __init__(
        self,
        scene: "Scene",
        title: str = "Undefined Node",
        inputs: list[int] | None = None,
        outputs: list[int] | None = None,
    ):
        """Initialize node.

        Args:
            scene: Reference to parent Scene
            title: Node title shown in scene
            inputs: List of socket types for inputs
            outputs: List of socket types for outputs
        """
        super().__init__()
        self._title = title
        self.scene = scene

        # Initialize variables
        self.content: QDMNodeContentWidget | None = None
        self.grNode: QDMGraphicsNode | None = None

        self.initInnerClasses()
        self.initSettings()

        self.title = title

        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)

        # Create sockets for inputs and outputs
        self.inputs: list[Socket] = []
        self.outputs: list[Socket] = []
        self.initSockets(inputs or [], outputs or [])

        # Dirty and evaluation flags
        self._is_dirty = False
        self._is_invalid = False

    def __str__(self) -> str:
        return (
            f"<{self.title}:{self.__class__.__name__} {hex(id(self))[2:5]}..{hex(id(self))[-3:]}>"
        )

    @property
    def title(self) -> str:
        """Node title shown in the scene.

        Returns:
            Current node title
        """
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """Set node title.

        Args:
            value: New title
        """
        self._title = value
        self.grNode.title = self._title

    @property
    def pos(self) -> "QPointF":
        """Retrieve node's position in the scene.

        Returns:
            QPointF with node position
        """
        return self.grNode.pos()

    def setPos(self, x: float, y: float) -> None:
        """Set position of the graphics node.

        Args:
            x: X scene position
            y: Y scene position
        """
        self.grNode.setPos(x, y)
        # Update all connected edges
        for socket in self.inputs:
            for edge in socket.edges:
                edge.grEdge.calcPath()
                edge.updatePositions()
        for socket in self.outputs:
            for edge in socket.edges:
                edge.grEdge.calcPath()
                edge.updatePositions()

    def initInnerClasses(self) -> None:
        """Set up graphics node and content widget."""
        node_content_class = self.getNodeContentClass()
        graphics_node_class = self.getGraphicsNodeClass()
        if node_content_class is not None:
            self.content = node_content_class(self)
        if graphics_node_class is not None:
            self.grNode = graphics_node_class(self)

    def getNodeContentClass(self) -> type["QDMNodeContentWidget"] | None:
        """Get class for node content widget.

        Returns:
            Content widget class
        """
        return self.__class__.NodeContent_class

    def getGraphicsNodeClass(self) -> type["QDMGraphicsNode"] | None:
        """Get class for graphics node.

        Returns:
            Graphics node class
        """
        return self.__class__.GraphicsNode_class

    def initSettings(self) -> None:
        """Initialize socket properties and positions."""
        self.socket_spacing = 22

        self.input_socket_position = LEFT_BOTTOM
        self.output_socket_position = RIGHT_TOP
        self.input_multi_edged = False
        self.output_multi_edged = True
        self.socket_offsets = {
            LEFT_BOTTOM: -1,
            LEFT_CENTER: -1,
            LEFT_TOP: -1,
            RIGHT_BOTTOM: 1,
            RIGHT_CENTER: 1,
            RIGHT_TOP: 1,
        }

    def initSockets(self, inputs: list[int], outputs: list[int], reset: bool = True) -> None:
        """Create sockets for inputs and outputs.

        Args:
            inputs: List of socket types (int)
            outputs: List of socket types (int)
            reset: If True, destroys and removes old sockets
        """
        if reset:
            # Clear old sockets
            if hasattr(self, "inputs") and hasattr(self, "outputs"):
                # Remove graphics sockets from scene
                for socket in self.inputs + self.outputs:
                    self.scene.grScene.removeItem(socket.grSocket)
                self.inputs = []
                self.outputs = []

        # Create new input sockets
        for counter, item in enumerate(inputs):
            socket = self.__class__.Socket_class(
                node=self,
                index=counter,
                position=self.input_socket_position,
                socket_type=item,
                multi_edges=self.input_multi_edged,
                count_on_this_node_side=len(inputs),
                is_input=True,
            )
            self.inputs.append(socket)

        # Create new output sockets
        for counter, item in enumerate(outputs):
            socket = self.__class__.Socket_class(
                node=self,
                index=counter,
                position=self.output_socket_position,
                socket_type=item,
                multi_edges=self.output_multi_edged,
                count_on_this_node_side=len(outputs),
                is_input=False,
            )
            self.outputs.append(socket)

    def onEdgeConnectionChanged(self, new_edge: "Edge") -> None:
        """Event handler when any connection (Edge) has changed.

        Override this to handle edge connection changes.

        Args:
            new_edge: Reference to the changed Edge
        """

    def onInputChanged(self, _socket: Socket) -> None:
        """Event handler when node's input edge has changed.

        Auto-marks this node and descendants as dirty.

        Args:
            socket: Reference to the changed Socket
        """
        self.markDirty()
        self.markDescendantsDirty()

    def onDeserialized(self, data: dict) -> None:
        """Event manually called when node was deserialized.

        Override to handle post-deserialization logic.

        Args:
            data: Dictionary containing deserialized data
        """

    def onDoubleClicked(self, event) -> None:
        """Event handler for double click on graphics node.

        Override to handle double click events.

        Args:
            event: Qt mouse event
        """

    def doSelect(self, new_state: bool = True) -> None:
        """Select or deselect the node.

        Args:
            new_state: True to select, False to deselect
        """
        self.grNode.doSelect(new_state)

    def isSelected(self) -> bool:
        """Check if node is selected.

        Returns:
            True if node is selected
        """
        return self.grNode.isSelected()

    def hasConnectedEdge(self, edge: "Edge") -> bool:
        """Check if edge is connected to any socket of this node.

        Args:
            edge: Edge to check

        Returns:
            True if edge is connected
        """
        return any(socket.isConnected(edge) for socket in self.inputs + self.outputs)

    def getSocketPosition(
        self, index: int, position: int, num_out_of: int = 1
    ) -> tuple[float, float]:
        """Get relative x, y position of a socket.

        Used for placing graphics sockets on graphics node.

        Args:
            index: Order number of the socket (0, 1, 2, ...)
            position: Socket position constant
            num_out_of: Total number of sockets on this position

        Returns:
            (x, y) position of socket on the node
        """
        x = (
            self.socket_offsets[position]
            if (position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM))
            else self.grNode.width + self.socket_offsets[position]
        )

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            # Start from bottom
            y = (
                self.grNode.height
                - self.grNode.edge_roundness
                - self.grNode.title_vertical_padding
                - index * self.socket_spacing
            )
        elif position in (LEFT_CENTER, RIGHT_CENTER):
            # Center position
            node_height = self.grNode.height
            top_offset = (
                self.grNode.title_height
                + 2 * self.grNode.title_vertical_padding
                + self.grNode.edge_padding
            )
            available_height = node_height - top_offset

            y = top_offset + available_height / 2.0 + (index - 0.5) * self.socket_spacing
            if num_out_of > 1:
                y -= self.socket_spacing * (num_out_of - 1) / 2

        elif position in (LEFT_TOP, RIGHT_TOP):
            # Start from top
            y = (
                self.grNode.title_height
                + self.grNode.title_vertical_padding
                + self.grNode.edge_roundness
                + index * self.socket_spacing
            )
        else:
            # This should never happen
            y = 0

        return (x, y)

    def getSocketScenePosition(self, socket: Socket) -> tuple[float, float]:
        """Get absolute socket position in the scene.

        Args:
            socket: Socket to get position for

        Returns:
            (x, y) socket's scene position
        """
        nodepos = self.grNode.pos()
        socketpos = self.getSocketPosition(
            socket.index, socket.position, socket.count_on_this_node_side
        )
        return (nodepos.x() + socketpos[0], nodepos.y() + socketpos[1])

    def updateConnectedEdges(self) -> None:
        """Recalculate positions of all connected edges."""
        for socket in self.inputs + self.outputs:
            for edge in socket.edges:
                edge.updatePositions()

    def remove(self) -> None:
        """Safely remove this node."""
        if DEBUG:
            pass
        if DEBUG:
            pass
        for socket in self.inputs + self.outputs:
            for edge in socket.edges.copy():
                if DEBUG:
                    pass
                edge.remove()
        if DEBUG:
            pass
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None
        if DEBUG:
            pass
        self.scene.removeNode(self)
        if DEBUG:
            pass

    # Node evaluation methods

    def isDirty(self) -> bool:
        """Check if node is marked as dirty.

        Returns:
            True if node is dirty
        """
        return self._is_dirty

    def markDirty(self, new_value: bool = True) -> None:
        """Mark this node as dirty.

        Args:
            new_value: True to mark dirty, False to un-dirty
        """
        self._is_dirty = new_value
        if self._is_dirty:
            self.onMarkedDirty()

    def onMarkedDirty(self) -> None:
        """Called when node has been marked as dirty.

        Override to handle dirty state changes.
        """

    def markChildrenDirty(self, new_value: bool = True) -> None:
        """Mark all first level children as dirty.

        Args:
            new_value: True to mark dirty, False to un-dirty
        """
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)

    def markDescendantsDirty(self, new_value: bool = True) -> None:
        """Mark all children and descendants as dirty.

        Args:
            new_value: True to mark dirty, False to un-dirty
        """
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)
            other_node.markDescendantsDirty(new_value)

    def isInvalid(self) -> bool:
        """Check if node is marked as invalid.

        Returns:
            True if node is invalid
        """
        return self._is_invalid

    def markInvalid(self, new_value: bool = True) -> None:
        """Mark this node as invalid.

        Args:
            new_value: True to mark invalid, False to make valid
        """
        self._is_invalid = new_value
        if self._is_invalid:
            self.onMarkedInvalid()

    def onMarkedInvalid(self) -> None:
        """Called when node has been marked as invalid.

        Override to handle invalid state changes.
        """

    def markChildrenInvalid(self, new_value: bool = True) -> None:
        """Mark all first level children as invalid.

        Args:
            new_value: True to mark invalid, False to make valid
        """
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)

    def markDescendantsInvalid(self, new_value: bool = True) -> None:
        """Mark all children and descendants as invalid.

        Args:
            new_value: True to mark invalid, False to make valid
        """
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)
            other_node.markDescendantsInvalid(new_value)

    def eval(self, _index: int = 0):
        """Evaluate this node.

        Override this method to implement node evaluation logic.

        Args:
            index: Socket index for evaluation

        Returns:
            Evaluation result (type depends on node)
        """
        self.markDirty(False)
        self.markInvalid(False)
        return 0

    def evalChildren(self) -> None:
        """Evaluate all children of this node."""
        for node in self.getChildrenNodes():
            node.eval()

    # Node traversal methods

    def getChildrenNodes(self) -> list["Node"]:
        """Get all first-level children connected to outputs.

        Returns:
            List of nodes connected to this node's outputs
        """
        if not self.outputs:
            return []
        other_nodes = []
        for output_socket in self.outputs:
            for edge in output_socket.edges:
                other_node = edge.getOtherSocket(output_socket).node
                other_nodes.append(other_node)
        return other_nodes

    def getInput(self, index: int = 0) -> "Node | None":
        """Get first node connected to input at index.

        Args:
            index: Order number of the input socket

        Returns:
            Node connected to specified input or None
        """
        try:
            input_socket = self.inputs[index]
            if len(input_socket.edges) == 0:
                return None
            connecting_edge = input_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node
        except Exception as e:
            dumpException(e)
            return None

    def getInputWithSocket(self, index: int = 0) -> tuple["Node | None", "Socket | None"]:
        """Get first node and socket connected to input at index.

        Args:
            index: Order number of the input socket

        Returns:
            Tuple of (Node, Socket) or (None, None)
        """
        try:
            input_socket = self.inputs[index]
            if len(input_socket.edges) == 0:
                return None, None
            connecting_edge = input_socket.edges[0]
            other_socket = connecting_edge.getOtherSocket(self.inputs[index])
            return other_socket.node, other_socket
        except Exception as e:
            dumpException(e)
            return None, None

    def getInputWithSocketIndex(self, index: int = 0) -> tuple["Node | None", int | None]:
        """Get first node and socket index connected to input at index.

        Args:
            index: Order number of the input socket

        Returns:
            Tuple of (Node, socket_index) or (None, None)
        """
        try:
            edge = self.inputs[index].edges[0]
            socket = edge.getOtherSocket(self.inputs[index])
            return socket.node, socket.index
        except IndexError:
            return None, None
        except Exception as e:
            dumpException(e)
            return None, None

    def getInputs(self, index: int = 0) -> list["Node"]:
        """Get all nodes connected to input at index.

        Args:
            index: Order number of the input socket

        Returns:
            List of nodes connected to specified input
        """
        ins = []
        for edge in self.inputs[index].edges:
            other_socket = edge.getOtherSocket(self.inputs[index])
            ins.append(other_socket.node)
        return ins

    def getOutputs(self, index: int = 0) -> list["Node"]:
        """Get all nodes connected to output at index.

        Args:
            index: Order number of the output socket

        Returns:
            List of nodes connected to specified output
        """
        outs = []
        for edge in self.outputs[index].edges:
            other_socket = edge.getOtherSocket(self.outputs[index])
            outs.append(other_socket.node)
        return outs

    # Serialization methods

    def serialize(self) -> OrderedDict:
        """Serialize node to dictionary.

        Returns:
            OrderedDict with node data
        """
        inputs, outputs = [], []
        for socket in self.inputs:
            inputs.append(socket.serialize())
        for socket in self.outputs:
            outputs.append(socket.serialize())
        ser_content = self.content.serialize() if isinstance(self.content, Serializable) else {}
        return OrderedDict(
            [
                ("id", self.id),
                ("title", self.title),
                ("pos_x", self.grNode.scenePos().x()),
                ("pos_y", self.grNode.scenePos().y()),
                ("inputs", inputs),
                ("outputs", outputs),
                ("content", ser_content),
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
        """Deserialize node from dictionary.

        Args:
            data: Dictionary with node data
            hashmap: Map of IDs to objects
            restore_id: Whether to restore the ID

        Returns:
            True if successful
        """
        if hashmap is None:
            hashmap = {}

        try:
            if restore_id:
                self.id = data["id"]
            hashmap[data["id"]] = self

            self.setPos(data["pos_x"], data["pos_y"])
            self.title = data["title"]

            # Sort sockets by index and position
            data["inputs"].sort(key=lambda socket: socket["index"] + socket["position"] * 10000)
            data["outputs"].sort(key=lambda socket: socket["index"] + socket["position"] * 10000)
            num_inputs = len(data["inputs"])
            num_outputs = len(data["outputs"])

            # Deserialize input sockets
            for socket_data in data["inputs"]:
                found = None
                for socket in self.inputs:
                    if socket.index == socket_data["index"]:
                        found = socket
                        break
                if found is None:
                    # Create new socket
                    found = self.__class__.Socket_class(
                        node=self,
                        index=socket_data["index"],
                        position=socket_data["position"],
                        socket_type=socket_data["socket_type"],
                        count_on_this_node_side=num_inputs,
                        is_input=True,
                    )
                    self.inputs.append(found)
                found.deserialize(socket_data, hashmap, restore_id)

            # Deserialize output sockets
            for socket_data in data["outputs"]:
                found = None
                for socket in self.outputs:
                    if socket.index == socket_data["index"]:
                        found = socket
                        break
                if found is None:
                    # Create new socket
                    found = self.__class__.Socket_class(
                        node=self,
                        index=socket_data["index"],
                        position=socket_data["position"],
                        socket_type=socket_data["socket_type"],
                        count_on_this_node_side=num_outputs,
                        is_input=False,
                    )
                    self.outputs.append(found)
                found.deserialize(socket_data, hashmap, restore_id)

        except Exception as e:
            dumpException(e)

        # Deserialize content
        if isinstance(self.content, Serializable):
            res = self.content.deserialize(data["content"], hashmap)
            return res

        return True
