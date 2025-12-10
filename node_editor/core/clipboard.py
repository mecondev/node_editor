"""
Scene Clipboard - Copy/Paste functionality.

This module provides clipboard support for the node editor, allowing
users to copy, cut, and paste nodes and edges.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from node_editor.core.scene import Scene

DEBUG = False
DEBUG_PASTING = False


class SceneClipboard:
    """Class managing clipboard operations for a Scene.

    The clipboard system serializes selected nodes and edges, and can
    deserialize them back into the scene at a new position.

    Attributes:
        scene: Reference to the Scene being managed
    """

    def __init__(self, scene: Scene) -> None:
        """Initialize clipboard for a scene.

        Args:
            scene: Scene instance to manage clipboard for
        """
        self.scene = scene

    def serializeSelected(self, delete: bool = False) -> OrderedDict:
        """Serialize selected items in the scene.

        Args:
            delete: If True, delete selected items after serialization (cut operation)

        Returns:
            OrderedDict with serialized nodes and edges
        """
        if DEBUG:
            pass

        sel_nodes = []
        sel_edges = []
        sel_sockets = {}

        # Sort items into nodes and edges
        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                sel_nodes.append(item.node.serialize())
                for socket in (item.node.inputs + item.node.outputs):
                    sel_sockets[socket.id] = socket
            elif hasattr(item, 'edge'):
                # Import here to avoid circular dependency
                from node_editor.graphics.edge import QDMGraphicsEdge
                if isinstance(item, QDMGraphicsEdge):
                    sel_edges.append(item.edge)

        if DEBUG:
            pass

        # Remove edges not fully connected to selected nodes
        edges_to_remove = []
        for edge in sel_edges:
            if (edge.start_socket.id in sel_sockets and
                edge.end_socket.id in sel_sockets):
                # Edge is connected on both sides
                pass
            else:
                if DEBUG:
                    pass
                edges_to_remove.append(edge)

        for edge in edges_to_remove:
            sel_edges.remove(edge)

        # Serialize edges
        edges_final = []
        for edge in sel_edges:
            edges_final.append(edge.serialize())

        if DEBUG:
            pass

        data = OrderedDict([
            ('nodes', sel_nodes),
            ('edges', edges_final),
        ])

        # If cut operation, delete selected items
        if delete:
            self.scene.getView().deleteSelected()
            self.scene.history.storeHistory("Cut out elements from scene", setModified=True)

        return data

    def deserializeFromClipboard(self, data: dict, *args, **kwargs) -> None:
        """Deserialize data from clipboard into the scene.

        Args:
            data: Dictionary with serialized nodes and edges
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        hashmap = {}

        # Get mouse position in scene coordinates
        view = self.scene.getView()
        mouse_scene_pos = view.last_scene_mouse_position

        # Calculate bounding box of copied nodes
        minx = maxx = miny = maxy = None

        for node_data in data['nodes']:
            # Handle both pos_x/pos_y and pos formats
            if 'pos_x' in node_data and 'pos_y' in node_data:
                x, y = node_data['pos_x'], node_data['pos_y']
            else:
                x, y = node_data['pos']

            if minx is None or x < minx:
                minx = x
            if maxx is None or x > maxx:
                maxx = x
            if miny is None or y < miny:
                miny = y
            if maxy is None or y > maxy:
                maxy = y

        # Adjust for node size
        if maxx is not None:
            maxx -= 180
        if maxy is not None:
            maxy += 100

        # Calculate relative bounding box center
        (minx + maxx) / 2 - minx if minx is not None and maxx is not None else 0

        (miny + maxy) / 2 - miny if miny is not None and maxy is not None else 0

        if DEBUG_PASTING:
            pass

        # Get mouse position
        mousex = mouse_scene_pos.x()
        mousey = mouse_scene_pos.y()

        # Suppress selection events during paste
        self.scene.setSilentSelectionEvents()
        self.scene.doDeselectItems()

        # Create each node
        created_nodes = []

        for node_data in data['nodes']:
            NodeClass = self.scene.getNodeClassFromData(node_data)
            new_node = NodeClass(self.scene)
            new_node.deserialize(node_data, hashmap, restore_id=False, *args, **kwargs)
            created_nodes.append(new_node)

            # Adjust node position relative to mouse
            posx = new_node.pos.x()
            posy = new_node.pos.y()

            if minx is not None and miny is not None:
                newx = mousex + posx - minx
                newy = mousey + posy - miny
            else:
                newx = posx
                newy = posy

            new_node.setPos(newx, newy)
            new_node.doSelect()

            if DEBUG_PASTING:
                pass

        # Create each edge
        if 'edges' in data:
            from node_editor.core.edge import Edge

            for edge_data in data['edges']:
                new_edge = Edge(self.scene)
                new_edge.deserialize(edge_data, hashmap, restore_id=False, *args, **kwargs)

        # Re-enable selection events
        self.scene.setSilentSelectionEvents(False)

        # Store history
        self.scene.history.storeHistory("Pasted elements in scene", setModified=True)
