#!/usr/bin/env python
"""Tests for Node class functionality.

Tests node creation, socket management, positioning, and lifecycle.

Author:
    Michael Economou

Date:
    2025-12-12
"""

from node_editor.core.node import Node


class TestNodeCreation:
    """Test node creation and initialization."""

    def test_create_basic_node(self, scene):
        """Test creating a node with default parameters."""
        node = Node(scene, "Test Node")

        assert node.title == "Test Node"
        assert node.scene == scene
        assert node in scene.nodes
        assert node.graphics_node is not None

    def test_create_node_with_sockets(self, scene):
        """Test creating a node with input and output sockets."""
        node = Node(scene, "Test Node", inputs=[0, 1], outputs=[2, 3])

        assert len(node.inputs) == 2
        assert len(node.outputs) == 2
        assert node.inputs[0].socket_type == 0
        assert node.inputs[1].socket_type == 1
        assert node.outputs[0].socket_type == 2
        assert node.outputs[1].socket_type == 3

    def test_node_has_unique_id(self, scene):
        """Test that each node gets a unique ID."""
        node1 = Node(scene, "Node 1")
        node2 = Node(scene, "Node 2")

        assert node1.id != node2.id

    def test_node_string_representation(self, scene):
        """Test __str__ method returns proper format."""
        node = Node(scene, "Test Node")
        node_str = str(node)

        assert "Test Node" in node_str
        assert "Node" in node_str


class TestNodeProperties:
    """Test node property getters and setters."""

    def test_get_set_title(self, scene):
        """Test title property getter and setter."""
        node = Node(scene, "Initial Title")

        assert node.title == "Initial Title"

        node.title = "New Title"
        assert node.title == "New Title"

    def test_get_position(self, scene):
        """Test getting node position."""
        node = Node(scene, "Test Node")
        node.set_pos(100, 200)

        pos = node.pos
        assert pos.x() == 100
        assert pos.y() == 200

    def test_set_position(self, scene):
        """Test setting node position."""
        node = Node(scene, "Test Node")
        node.set_pos(150, 250)

        assert node.graphics_node.pos().x() == 150
        assert node.graphics_node.pos().y() == 250


class TestNodeSockets:
    """Test socket management on nodes."""

    def test_get_socket_position(self, scene):
        """Test socket position calculation."""
        node = Node(scene, "Test Node", inputs=[0, 1])

        # Should return valid position tuples
        pos = node.get_socket_position(0, 1, 2)
        assert isinstance(pos, tuple)
        assert len(pos) == 2

    def test_socket_has_parent_node(self, scene):
        """Test that sockets reference their parent node."""
        node = Node(scene, "Test Node", inputs=[0])

        assert node.inputs[0].node == node

    def test_update_connected_edges(self, scene):
        """Test updating edges when node moves."""
        node1 = Node(scene, "Node 1", outputs=[0])
        node2 = Node(scene, "Node 2", inputs=[0])

        # Create edge between nodes
        from node_editor.core.edge import Edge

        edge = Edge(scene, node1.outputs[0], node2.inputs[0])

        # Move node and update
        node1.set_pos(200, 200)
        node1.update_connected_edges()

        # Edge should still be connected
        assert edge in node1.outputs[0].edges


class TestNodeState:
    """Test node dirty and invalid state tracking."""

    def test_node_starts_clean(self, scene):
        """Test new nodes start in clean state."""
        node = Node(scene, "Test Node")

        assert not node.is_dirty()
        assert not node.is_invalid()

    def test_mark_node_dirty(self, scene):
        """Test marking node as dirty."""
        node = Node(scene, "Test Node")
        node.mark_dirty()

        assert node.is_dirty()

    def test_mark_node_invalid(self, scene):
        """Test marking node as invalid."""
        node = Node(scene, "Test Node")
        node.mark_invalid()

        assert node.is_invalid()

    def test_mark_descendants_dirty(self, scene):
        """Test marking descendant nodes dirty."""
        node1 = Node(scene, "Node 1", outputs=[0])
        node2 = Node(scene, "Node 2", inputs=[0], outputs=[0])
        node3 = Node(scene, "Node 3", inputs=[0])

        from node_editor.core.edge import Edge

        Edge(scene, node1.outputs[0], node2.inputs[0])
        Edge(scene, node2.outputs[0], node3.inputs[0])

        # Mark node1 dirty, should propagate
        node1.mark_dirty()
        node1.mark_descendants_dirty()

        assert node2.is_dirty()
        assert node3.is_dirty()


class TestNodeRemoval:
    """Test node deletion and cleanup."""

    def test_remove_node(self, scene):
        """Test removing a node from scene."""
        node = Node(scene, "Test Node")
        node_id = node.id

        node.remove()

        assert node not in scene.nodes
        assert all(n.id != node_id for n in scene.nodes)

    def test_remove_node_with_edges(self, scene):
        """Test removing node removes connected edges."""
        node1 = Node(scene, "Node 1", outputs=[0])
        node2 = Node(scene, "Node 2", inputs=[0])

        from node_editor.core.edge import Edge

        edge = Edge(scene, node1.outputs[0], node2.inputs[0])

        node1.remove()

        # Edge should be removed
        assert edge not in scene.edges
        assert len(node2.inputs[0].edges) == 0

    def test_remove_node_cleans_up(self, scene):
        """Test node removal cleans up properly."""
        node = Node(scene, "Test Node", inputs=[0])

        # Should not raise exceptions
        node.remove()
        assert node not in scene.nodes


class TestNodeSerialization:
    """Test node serialization and deserialization."""

    def test_serialize_node(self, scene):
        """Test serializing a node to dict."""
        node = Node(scene, "Test Node", inputs=[0, 1], outputs=[2])
        node.set_pos(100, 150)

        data = node.serialize()

        assert data["sid"] == node.sid
        assert data["title"] == "Test Node"
        assert data["pos_x"] == 100
        assert data["pos_y"] == 150
        assert len(data["inputs"]) == 2
        assert len(data["outputs"]) == 1

    def test_deserialize_node(self, scene):
        """Test deserializing a node from dict."""
        original = Node(scene, "Original Node", inputs=[0], outputs=[1])
        original.set_pos(200, 250)

        data = original.serialize()
        original.remove()

        # Create new node from data
        restored = Node(scene, "Temp")
        restored.deserialize(data, {}, True)

        assert restored.title == "Original Node"
        assert restored.pos.x() == 200
        assert restored.pos.y() == 250


class TestNodeCallbacks:
    """Test node event callbacks."""

    def test_on_input_changed_callback(self, scene):
        """Test on_input_changed callback is callable."""
        node = Node(scene, "Test Node", inputs=[0])

        # Should not raise exception
        node.on_input_changed(node.inputs[0])

    def test_on_edge_connection_changed(self, scene):
        """Test on_edge_connection_changed callback."""
        node1 = Node(scene, "Node 1", outputs=[0])
        node2 = Node(scene, "Node 2", inputs=[0])

        from node_editor.core.edge import Edge

        edge = Edge(scene, node1.outputs[0], node2.inputs[0])

        # Should not raise exception
        node1.on_edge_connection_changed(edge)
        node2.on_edge_connection_changed(edge)
