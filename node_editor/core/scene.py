"""
Scene - Central container for nodes and edges.

This module contains the Scene class which manages all nodes, edges, history,
and clipboard in a node-based visual programming graph.
"""

from __future__ import annotations

import json
import os
from collections import OrderedDict
from collections.abc import Callable
from typing import TYPE_CHECKING

from node_editor.core.serializable import Serializable
from node_editor.utils.helpers import dump_exception

if TYPE_CHECKING:
    from PyQt5.QtCore import QPointF
    from PyQt5.QtWidgets import QGraphicsView

    from node_editor.core.edge import Edge
    from node_editor.core.node import Node
    from node_editor.graphics.scene import QDMGraphicsScene


# Debug flag for warnings
DEBUG_REMOVE_WARNINGS = False


class InvalidFile(Exception):
    """Exception raised when a file cannot be loaded."""


class Scene(Serializable):
    """Class representing NodeEditor's Scene.

    The Scene is the central container that manages all nodes and edges in the graph.
    It provides serialization, history management, clipboard support, and event handling.

    Attributes:
        nodes: List of Node instances in this scene
        edges: List of Edge instances in this scene
        history: SceneHistory instance for undo/redo
        clipboard: SceneClipboard instance for copy/paste
        scene_width: Width of the scene in pixels (default: 64000)
        scene_height: Height of the scene in pixels (default: 64000)
        filename: Current filename associated with this scene
        grScene: QDMGraphicsScene instance for visual representation
    """

    # Class attributes for dependency injection
    historyClass = None  # Set after imports
    clipboardClass = None  # Set after imports

    def __init__(self) -> None:
        """Initialize a new Scene."""
        super().__init__()

        # Node and edge containers
        self.nodes: list[Node] = []
        self.edges: list[Edge] = []

        # File association
        self.filename: str | None = None

        # Scene dimensions
        self.scene_width: int = 64000
        self.scene_height: int = 64000

        # Internal state flags
        self._silent_selection_events: bool = False
        self._has_been_modified: bool = False
        self._last_selected_items: list | None = None

        # Event listeners
        self._has_been_modified_listeners: list[Callable] = []
        self._item_selected_listeners: list[Callable] = []
        self._items_deselected_listeners: list[Callable] = []

        # Node class selector for deserialization
        self.node_class_selector: Callable[[dict], type[Node]] | None = None

        # Initialize UI and components
        self.initUI()

        # Late import to avoid circular dependencies
        from node_editor.core.clipboard import SceneClipboard
        from node_editor.core.history import SceneHistory

        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)

        # Connect graphics scene signals
        self.grScene.itemSelected.connect(self.onItemSelected)
        self.grScene.itemsDeselected.connect(self.onItemsDeselected)

    @property
    def has_been_modified(self) -> bool:
        """Check if the scene has been modified.

        Returns:
            True if the scene has been modified since last save
        """
        return self._has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value: bool) -> None:
        """Set the modified state and trigger listeners.

        Args:
            value: New modified state
        """
        if not self._has_been_modified and value:
            # Set it now, because we will be reading it soon
            self._has_been_modified = value

            # Call all registered listeners
            for callback in self._has_been_modified_listeners:
                callback()

        self._has_been_modified = value

    def initUI(self) -> None:
        """Initialize the graphics scene."""
        from node_editor.graphics.scene import QDMGraphicsScene

        self.grScene: QDMGraphicsScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)

    # Node and edge management

    def addNode(self, node: Node) -> None:
        """Add a node to this scene.

        Args:
            node: Node instance to add
        """
        self.nodes.append(node)

    def addEdge(self, edge: Edge) -> None:
        """Add an edge to this scene.

        Args:
            edge: Edge instance to add
        """
        self.edges.append(edge)

    def removeNode(self, node: Node) -> None:
        """Remove a node from this scene.

        Args:
            node: Node instance to remove
        """
        if node in self.nodes:
            self.nodes.remove(node)
        elif DEBUG_REMOVE_WARNINGS:
            pass

    def removeEdge(self, edge: Edge) -> None:
        """Remove an edge from this scene.

        Args:
            edge: Edge instance to remove
        """
        if edge in self.edges:
            self.edges.remove(edge)
        elif DEBUG_REMOVE_WARNINGS:
            pass

    def clear(self) -> None:
        """Remove all nodes from this scene. This also removes all edges."""
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        self.has_been_modified = False

    def getNodeByID(self, node_id: int) -> Node | None:
        """Find a node in the scene by its ID.

        Args:
            node_id: ID of the node to find

        Returns:
            Found Node instance or None
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    # Selection management

    def setSilentSelectionEvents(self, value: bool = True) -> None:
        """Suppress onItemSelected events.

        This is useful when working with the clipboard to avoid triggering
        unwanted selection events.

        Args:
            value: True to suppress events, False to enable them
        """
        self._silent_selection_events = value

    def getSelectedItems(self) -> list:
        """Get currently selected graphics items.

        Returns:
            List of selected QGraphicsItem instances
        """
        return self.grScene.selectedItems()

    def doDeselectItems(self, silent: bool = False) -> None:
        """Deselect all items in the scene.

        Args:
            silent: If True, onItemsDeselected won't be called
        """
        for item in self.getSelectedItems():
            item.setSelected(False)
        if not silent:
            self.onItemsDeselected()

    def resetLastSelectedStates(self) -> None:
        """Reset internal selected flags in all nodes and edges."""
        for node in self.nodes:
            node.grNode._last_selected_state = False
        for edge in self.edges:
            edge.grEdge._last_selected_state = False

    def onItemSelected(self, silent: bool = False) -> None:
        """Handle item selection and trigger event listeners.

        Args:
            silent: If True, callbacks won't be called and history won't be stored
        """
        if self._silent_selection_events:
            return

        current_selected_items = self.getSelectedItems()
        if current_selected_items != self._last_selected_items:
            self._last_selected_items = current_selected_items
            if not silent:
                # Run all callbacks first
                for callback in self._item_selected_listeners:
                    callback()
                # Store history as the last step
                self.history.storeHistory("Selection Changed")

    def onItemsDeselected(self, silent: bool = False) -> None:
        """Handle items deselection and trigger event listeners.

        Args:
            silent: If True, callbacks won't be called and history won't be stored
        """
        # Check if selection actually changed
        current_selected_items = self.getSelectedItems()
        if current_selected_items == self._last_selected_items:
            return

        self.resetLastSelectedStates()
        if current_selected_items == []:
            self._last_selected_items = []
            if not silent:
                self.history.storeHistory("Deselected Everything")
                for callback in self._items_deselected_listeners:
                    callback()

    # Modification state

    def isModified(self) -> bool:
        """Check if the scene has been modified.

        Returns:
            True if the scene has been modified
        """
        return self.has_been_modified

    # Event listener management

    def addHasBeenModifiedListener(self, callback: Callable) -> None:
        """Register a callback for the 'Has Been Modified' event.

        Args:
            callback: Function to call when the scene is modified
        """
        self._has_been_modified_listeners.append(callback)

    def addItemSelectedListener(self, callback: Callable) -> None:
        """Register a callback for the 'Item Selected' event.

        Args:
            callback: Function to call when an item is selected
        """
        self._item_selected_listeners.append(callback)

    def addItemsDeselectedListener(self, callback: Callable) -> None:
        """Register a callback for the 'Items Deselected' event.

        Args:
            callback: Function to call when items are deselected
        """
        self._items_deselected_listeners.append(callback)

    def addDragEnterListener(self, callback: Callable) -> None:
        """Register a callback for the 'Drag Enter' event.

        Args:
            callback: Function to call when a drag enters the view
        """
        self.getView().addDragEnterListener(callback)

    def addDropListener(self, callback: Callable) -> None:
        """Register a callback for the 'Drop' event.

        Args:
            callback: Function to call when a drop occurs
        """
        self.getView().addDropListener(callback)

    # View access

    def getView(self) -> QGraphicsView:
        """Get the QGraphicsView attached to this scene.

        Returns:
            QGraphicsView instance
        """
        return self.grScene.views()[0]

    def getItemAt(self, pos: QPointF):
        """Get the graphics item at the given scene position.

        Args:
            pos: Scene position

        Returns:
            QGraphicsItem at the position or None
        """
        return self.getView().itemAt(pos)

    # File operations

    def saveToFile(self, filename: str) -> None:
        """Save this scene to a file on disk.

        Args:
            filename: Path where to save the scene
        """
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))

        self.has_been_modified = False
        self.filename = filename

    def loadFromFile(self, filename: str) -> None:
        """Load this scene from a file on disk.

        Args:
            filename: Path from where to load the scene

        Raises:
            InvalidFile: If the file cannot be decoded as JSON
        """
        with open(filename) as file:
            raw_data = file.read()
            try:
                data = json.loads(raw_data)
                self.filename = filename
                self.deserialize(data)
                self.has_been_modified = False
            except json.JSONDecodeError:
                raise InvalidFile(f"{os.path.basename(filename)} is not a valid JSON file")
            except Exception as e:
                dump_exception(e)

    # Node/Edge class selection

    def getEdgeClass(self) -> type[Edge]:
        """Get the Edge class to use for this scene.

        Override this method to use a custom Edge class.

        Returns:
            Edge class type
        """
        from node_editor.core.edge import Edge
        return Edge

    def setNodeClassSelector(self, class_selecting_function: Callable[[dict], type[Node]]) -> None:
        """Set the function that determines which Node class to instantiate during deserialization.

        If not set, the base Node class will always be used.

        Args:
            class_selecting_function: Function that returns a Node class type based on serialized data
        """
        self.node_class_selector = class_selecting_function

    def getNodeClassFromData(self, data: dict) -> type[Node]:
        """Determine which Node class to instantiate based on serialized data.

        Args:
            data: Serialized node data

        Returns:
            Node class type to instantiate
        """
        from node_editor.core.node import Node

        if self.node_class_selector is None:
            return Node
        return self.node_class_selector(data)

    # Serialization

    def serialize(self) -> OrderedDict:
        """Serialize the scene to a dictionary.

        Returns:
            OrderedDict with scene data including all nodes and edges
        """
        nodes = []
        edges = []

        # Serialize all nodes (avoiding duplicates)
        for node in self.nodes:
            newnode = node.serialize()
            if not any(newnode['id'] == a['id'] for a in nodes):
                nodes.append(newnode)

        # Serialize all edges (avoiding duplicates)
        for edge in self.edges:
            newedge = edge.serialize()
            if not any(newedge['id'] == a['id'] for a in edges):
                edges.append(newedge)

        return OrderedDict([
            ('id', self.id),
            ('scene_width', self.scene_width),
            ('scene_height', self.scene_height),
            ('nodes', nodes),
            ('edges', edges),
        ])

    def deserialize(
        self,
        data: dict,
        hashmap: dict | None = None,
        restore_id: bool = True,
        *args,
        **kwargs
    ) -> bool:
        """Deserialize the scene from a dictionary.

        This method reuses existing nodes and edges when possible instead of
        recreating everything from scratch.

        Args:
            data: Dictionary with scene data
            hashmap: Hashmap for tracking deserialized objects
            restore_id: Whether to restore the scene ID
            *args: Additional arguments
            **kwargs: Additional keyword arguments

        Returns:
            True if deserialization succeeded
        """
        if hashmap is None:
            hashmap = {}

        if restore_id:
            self.id = data['id']

        # Deserialize NODES
        # Reuse existing nodes when possible
        all_nodes = self.nodes.copy()

        for node_data in data['nodes']:
            # Try to find this node in the scene
            found = None
            for node in all_nodes:
                if node.id == node_data['id']:
                    found = node
                    break

            if not found:
                # Create new node
                try:
                    NodeClass = self.getNodeClassFromData(node_data)
                    new_node = NodeClass(self)
                    new_node.deserialize(node_data, hashmap, restore_id, *args, **kwargs)
                    new_node.onDeserialized(node_data)
                except Exception as e:
                    dump_exception(e)
            else:
                # Reuse existing node
                try:
                    found.deserialize(node_data, hashmap, restore_id, *args, **kwargs)
                    found.onDeserialized(node_data)
                    all_nodes.remove(found)
                except Exception as e:
                    dump_exception(e)

        # Remove nodes that are left in the scene but were not in the serialized data
        while all_nodes:
            node = all_nodes.pop()
            node.remove()

        # Deserialize EDGES
        # Reuse existing edges when possible
        all_edges = self.edges.copy()

        for edge_data in data['edges']:
            # Try to find this edge in the scene
            found = None
            for edge in all_edges:
                if edge.id == edge_data['id']:
                    found = edge
                    break

            if not found:
                # Create new edge
                EdgeClass = self.getEdgeClass()
                new_edge = EdgeClass(self)
                new_edge.deserialize(edge_data, hashmap, restore_id, *args, **kwargs)
            else:
                # Reuse existing edge
                found.deserialize(edge_data, hashmap, restore_id, *args, **kwargs)
                all_edges.remove(found)

        # Remove edges that are left in the scene but were not in the serialized data
        while all_edges:
            edge = all_edges.pop()
            edge.remove()

        return True
