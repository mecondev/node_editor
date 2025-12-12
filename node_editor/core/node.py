"""Node representation in the visual graph editor.

This module defines the Node class, the fundamental building block of node
graphs. Nodes contain sockets for connections, content widgets for UI
interaction, and graphics representations for visualization. The module
supports an evaluation system with dirty/invalid state tracking for
efficient graph computation.

Node Features:
    - Configurable input and output sockets
    - Customizable content widget
    - Dirty/invalid state propagation for evaluation
    - Serialization/deserialization support
    - Graph traversal methods

Author:
    Michael Economou

Date:
    2025-12-11
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


class Node(Serializable):
    """Fundamental graph element containing sockets and content.

    A node represents a single processing unit in the graph. It manages
    input and output sockets for connections, a content widget for user
    interaction, and maintains evaluation state (dirty/invalid) for
    efficient graph computation.

    Subclass this to create custom node types with specific behavior,
    socket configurations, and content widgets.

    Attributes:
        scene: Parent Scene containing this node.
        title: Display title shown in the graphics node.
        grNode: QDMGraphicsNode instance for visualization.
        content: QDMNodeContentWidget instance for UI content.
        inputs: List of input Socket instances.
        outputs: List of output Socket instances.

    Class Attributes:
        GraphicsNode_class: Graphics class for node visualization.
        NodeContent_class: Content widget class for node UI.
        Socket_class: Socket class for creating connections.
    """

    GraphicsNode_class: type["QDMGraphicsNode"] | None = None
    NodeContent_class: type["QDMNodeContentWidget"] | None = None
    Socket_class = Socket

    def __init__(
        self,
        scene: "Scene",
        title: str = "Undefined Node",
        inputs: list[int] | None = None,
        outputs: list[int] | None = None,
    ):
        """Create a node and add it to the scene.

        Initializes graphics, content widget, and sockets based on
        provided configurations. The node is automatically registered
        with the scene.

        Args:
            scene: Parent scene that will contain this node.
            title: Display text shown in the node header.
            inputs: Socket type identifiers for input sockets.
            outputs: Socket type identifiers for output sockets.
        """
        super().__init__()
        self._title = title
        self.scene = scene

        self.content: QDMNodeContentWidget | None = None
        self.grNode: QDMGraphicsNode | None = None

        self.initInnerClasses()
        self.initSettings()

        self.title = title

        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)

        self.inputs: list[Socket] = []
        self.outputs: list[Socket] = []
        self.initSockets(inputs or [], outputs or [])

        self._is_dirty = False
        self._is_invalid = False

    def __str__(self) -> str:
        """Return human-readable node representation.

        Returns:
            Format: <title:ClassName ID> showing title and class.
        """
        return (
            f"<{self.title}:{self.__class__.__name__} {hex(id(self))[2:5]}..{hex(id(self))[-3:]}>"
        )

    @property
    def title(self) -> str:
        """Display title shown in the graphics node header.

        Returns:
            Current title string.
        """
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """Update node title and refresh display.

        Args:
            value: New title to display.
        """
        self._title = value
        self.grNode.title = self._title

    @property
    def pos(self) -> "QPointF":
        """Current position in scene coordinates.

        Returns:
            QPointF with x, y position.
        """
        return self.grNode.pos()

    def setPos(self, x: float, y: float) -> None:
        """Move node to specified scene position.

        Updates graphics position and recalculates all connected
        edge paths.

        Args:
            x: Horizontal scene coordinate.
            y: Vertical scene coordinate.
        """
        self.grNode.setPos(x, y)
        for socket in self.inputs:
            for edge in socket.edges:
                edge.grEdge.calcPath()
                edge.updatePositions()
        for socket in self.outputs:
            for edge in socket.edges:
                edge.grEdge.calcPath()
                edge.updatePositions()

    def initInnerClasses(self) -> None:
        """Instantiate graphics node and content widget.

        Creates instances using class-level factory classes. Override
        getNodeContentClass() and getGraphicsNodeClass() to customize.
        """
        node_content_class = self.getNodeContentClass()
        graphics_node_class = self.getGraphicsNodeClass()
        if node_content_class is not None:
            self.content = node_content_class(self)
        if graphics_node_class is not None:
            self.grNode = graphics_node_class(self)

    def getNodeContentClass(self) -> type["QDMNodeContentWidget"] | None:
        """Get factory class for content widget.

        Override in subclasses to provide custom content widgets.

        Returns:
            Content widget class or None for no content.
        """
        return self.__class__.NodeContent_class

    def getGraphicsNodeClass(self) -> type["QDMGraphicsNode"] | None:
        """Get factory class for graphics node.

        Override in subclasses to provide custom graphics.

        Returns:
            Graphics node class or None.
        """
        return self.__class__.GraphicsNode_class

    def initSettings(self) -> None:
        """Configure socket layout properties.

        Sets socket spacing, positions, and multi-edge defaults.
        Override to customize socket arrangement.
        """
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
        """Create input and output sockets from type lists.

        Optionally removes existing sockets first. Each element in
        the lists represents a socket type identifier.

        Args:
            inputs: Socket type IDs for inputs.
            outputs: Socket type IDs for outputs.
            reset: If True, remove existing sockets before creating new.
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
        """Handle edge connection or disconnection events.

        Called when any edge connected to this node changes state.
        Override to implement custom connection handling logic.

        Args:
            new_edge: Edge that was connected or disconnected.
        """

    def onInputChanged(self, _socket: Socket) -> None:
        """Handle input socket value changes.

        Called when data arrives on an input socket. Default behavior
        marks this node and all descendants as dirty for re-evaluation.

        Args:
            _socket: Input socket that received new data.
        """
        self.markDirty()
        self.markDescendantsDirty()

    def onDeserialized(self, data: dict) -> None:
        """Handle post-deserialization initialization.

        Called after node state is restored from saved data. Override
        to perform any required setup after loading.

        Args:
            data: Dictionary containing the deserialized data.
        """

    def onDoubleClicked(self, event) -> None:
        """Handle double-click on graphics node.

        Override to implement custom double-click behavior such as
        opening configuration dialogs.

        Args:
            event: Qt mouse event with click details.
        """

    def doSelect(self, new_state: bool = True) -> None:
        """Programmatically select or deselect this node.

        Args:
            new_state: True to select, False to deselect.
        """
        self.grNode.doSelect(new_state)

    def isSelected(self) -> bool:
        """Check if node is currently selected.

        Returns:
            True if node is in selected state.
        """
        return self.grNode.isSelected()

    def hasConnectedEdge(self, edge: "Edge") -> bool:
        """Check if specified edge connects to this node.

        Args:
            edge: Edge to check for connection.

        Returns:
            True if edge is connected to any socket on this node.
        """
        return any(socket.isConnected(edge) for socket in self.inputs + self.outputs)

    def getSocketPosition(
        self, index: int, position: int, num_out_of: int = 1
    ) -> tuple[float, float]:
        """Calculate socket position in node-local coordinates.

        Determines placement based on socket index, position constant,
        and total socket count for proper spacing.

        Args:
            index: Zero-based socket index on this side.
            position: Position constant (LEFT_TOP, RIGHT_CENTER, etc.).
            num_out_of: Total sockets on this position for spacing calc.

        Returns:
            Tuple of (x, y) in node-local coordinates.
        """
        x = (
            self.socket_offsets[position]
            if (position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM))
            else self.grNode.width + self.socket_offsets[position]
        )

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            y = (
                self.grNode.height
                - self.grNode.edge_roundness
                - self.grNode.title_vertical_padding
                - index * self.socket_spacing
            )
        elif position in (LEFT_CENTER, RIGHT_CENTER):
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
            y = (
                self.grNode.title_height
                + self.grNode.title_vertical_padding
                + self.grNode.edge_roundness
                + index * self.socket_spacing
            )
        else:
            y = 0

        return (x, y)

    def getSocketScenePosition(self, socket: Socket) -> tuple[float, float]:
        """Calculate socket position in scene coordinates.

        Combines node position with socket offset for absolute placement.

        Args:
            socket: Socket to get position for.

        Returns:
            Tuple of (x, y) in scene coordinates.
        """
        nodepos = self.grNode.pos()
        socketpos = self.getSocketPosition(
            socket.index, socket.position, socket.count_on_this_node_side
        )
        return (nodepos.x() + socketpos[0], nodepos.y() + socketpos[1])

    def updateConnectedEdges(self) -> None:
        """Refresh positions of all edges connected to this node.

        Call after moving node to update edge path calculations.
        """
        for socket in self.inputs + self.outputs:
            for edge in socket.edges:
                edge.updatePositions()

    def remove(self) -> None:
        """Delete node and clean up all references.

        Removes all connected edges, graphics item, and unregisters
        from the scene.
        """
        for socket in self.inputs + self.outputs:
            for edge in socket.edges.copy():
                edge.remove()

        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None
        self.scene.removeNode(self)

    # Node evaluation methods

    def isDirty(self) -> bool:
        """Check if node requires re-evaluation.

        Returns:
            True if node data is stale and needs recalculation.
        """
        return self._is_dirty

    def markDirty(self, new_value: bool = True) -> None:
        """Set dirty state indicating need for re-evaluation.

        Triggers onMarkedDirty() callback when transitioning to dirty.

        Args:
            new_value: True to mark dirty, False to clear dirty state.
        """
        self._is_dirty = new_value
        if self._is_dirty:
            self.onMarkedDirty()

    def onMarkedDirty(self) -> None:
        """Handle transition to dirty state.

        Override to implement custom dirty-state handling such as
        visual indicators or logging.
        """

    def markChildrenDirty(self, new_value: bool = True) -> None:
        """Mark immediate downstream nodes as dirty.

        Only affects first-level children connected to outputs.

        Args:
            new_value: True to mark dirty, False to clear.
        """
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)

    def markDescendantsDirty(self, new_value: bool = True) -> None:
        """Recursively mark all downstream nodes as dirty.

        Propagates dirty state through entire downstream subgraph.

        Args:
            new_value: True to mark dirty, False to clear.
        """
        for other_node in self.getChildrenNodes():
            other_node.markDirty(new_value)
            other_node.markDescendantsDirty(new_value)

    def isInvalid(self) -> bool:
        """Check if node is in an error state.

        Returns:
            True if node has invalid configuration or data.
        """
        return self._is_invalid

    def markInvalid(self, new_value: bool = True) -> None:
        """Set invalid state indicating configuration error.

        Triggers onMarkedInvalid() callback when transitioning to invalid.

        Args:
            new_value: True to mark invalid, False to clear.
        """
        self._is_invalid = new_value
        if self._is_invalid:
            self.onMarkedInvalid()
        # Update visual representation
        if self.grNode:
            self.grNode.update()

    def onMarkedInvalid(self) -> None:
        """Handle transition to invalid state.

        Override to implement error indicators or recovery logic.
        """

    def markChildrenInvalid(self, new_value: bool = True) -> None:
        """Mark immediate downstream nodes as invalid.

        Args:
            new_value: True to mark invalid, False to clear.
        """
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)

    def markDescendantsInvalid(self, new_value: bool = True) -> None:
        """Recursively mark all downstream nodes as invalid.

        Args:
            new_value: True to mark invalid, False to clear.
        """
        for other_node in self.getChildrenNodes():
            other_node.markInvalid(new_value)
            other_node.markDescendantsInvalid(new_value)

    def eval(self, _index: int = 0):
        """Evaluate node and compute output value.

        Override this method to implement node-specific computation.
        Default implementation clears dirty/invalid state and returns 0.

        Args:
            _index: Output socket index to evaluate.

        Returns:
            Computed value (type depends on node implementation).
        """
        self.markDirty(False)
        self.markInvalid(False)
        return 0

    def evalChildren(self) -> None:
        """Evaluate all immediate downstream nodes.

        Calls eval() on each node connected to this node's outputs.
        """
        for node in self.getChildrenNodes():
            node.eval()

    # Node traversal methods

    def getChildrenNodes(self) -> list["Node"]:
        """Get nodes connected to this node's outputs.

        Returns:
            List of downstream nodes (immediate children only).
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
        """Get node connected to specified input socket.

        Returns only the first connected node if multiple exist.

        Args:
            index: Input socket index (0-based).

        Returns:
            Connected node or None if unconnected.
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
        """Get node and socket connected to specified input.

        Returns first connection if multiple exist.

        Args:
            index: Input socket index (0-based).

        Returns:
            Tuple of (node, socket) or (None, None) if unconnected.
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
        """Get node and output socket index connected to specified input.

        Args:
            index: Input socket index (0-based).

        Returns:
            Tuple of (node, socket_index) or (None, None) if unconnected.
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
        """Get all nodes connected to specified input socket.

        Useful for multi-edge input sockets.

        Args:
            index: Input socket index (0-based).

        Returns:
            List of all connected upstream nodes.
        """
        ins = []
        for edge in self.inputs[index].edges:
            other_socket = edge.getOtherSocket(self.inputs[index])
            ins.append(other_socket.node)
        return ins

    def getOutputs(self, index: int = 0) -> list["Node"]:
        """Get all nodes connected to specified output socket.

        Args:
            index: Output socket index (0-based).

        Returns:
            List of all connected downstream nodes.
        """
        outs = []
        for edge in self.outputs[index].edges:
            other_socket = edge.getOtherSocket(self.outputs[index])
            outs.append(other_socket.node)
        return outs

    # Serialization methods

    def serialize(self) -> OrderedDict:
        """Convert node state to ordered dictionary for persistence.

        Includes position, sockets, and content widget state.

        Returns:
            OrderedDict containing complete node configuration.
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
        """Restore node state from serialized dictionary.

        Restores position, sockets, and content. Uses hashmap to
        resolve ID references for edge connections.

        Args:
            data: Dictionary containing serialized node data.
            hashmap: Maps original IDs to restored objects.
            restore_id: If True, restore original ID from data.

        Returns:
            True on successful deserialization.
        """
        if hashmap is None:
            hashmap = {}

        try:
            if restore_id:
                self.id = data["id"]
            hashmap[data["id"]] = self

            self.setPos(data["pos_x"], data["pos_y"])
            self.title = data["title"]

            data["inputs"].sort(key=lambda socket: socket["index"] + socket["position"] * 10000)
            data["outputs"].sort(key=lambda socket: socket["index"] + socket["position"] * 10000)
            num_inputs = len(data["inputs"])
            num_outputs = len(data["outputs"])

            for socket_data in data["inputs"]:
                found = None
                for socket in self.inputs:
                    if socket.index == socket_data["index"]:
                        found = socket
                        break
                if found is None:
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

            for socket_data in data["outputs"]:
                found = None
                for socket in self.outputs:
                    if socket.index == socket_data["index"]:
                        found = socket
                        break
                if found is None:
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

        if isinstance(self.content, Serializable):
            res = self.content.deserialize(data["content"], hashmap)
            return res

        return True
