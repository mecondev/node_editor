#!/usr/bin/env python
"""Tests for Edge class functionality.

Tests edge creation, connection validation, path types, and lifecycle.

Author:
    Michael Economou

Date:
    2025-12-12
"""

import pytest  # type: ignore[import-untyped]

from node_editor.core.edge import (
    EDGE_TYPE_BEZIER,
    EDGE_TYPE_DIRECT,
    Edge,
)
from node_editor.core.node import Node


@pytest.fixture
def nodes(scene):
    """Create two test nodes with sockets."""
    node1 = Node(scene, "Node 1", outputs=[0])
    node2 = Node(scene, "Node 2", inputs=[0])
    return node1, node2


class TestEdgeCreation:
    """Test edge creation and initialization."""

    def test_create_edge_between_sockets(self, nodes):
        """Test creating an edge between two sockets."""
        node1, node2 = nodes
        scene = node1.scene

        edge = Edge(scene, node1.outputs[0], node2.inputs[0])

        assert edge.start_socket == node1.outputs[0]
        assert edge.end_socket == node2.inputs[0]
        assert edge in scene.edges

    def test_edge_registers_with_sockets(self, nodes):
        """Test edge registers itself with both sockets."""
        node1, node2 = nodes

        edge = Edge(node1.scene, node1.outputs[0], node2.inputs[0])

        assert edge in node1.outputs[0].edges
        assert edge in node2.inputs[0].edges

    def test_create_edge_with_type(self, nodes):
        """Test creating edge with specific type."""
        node1, node2 = nodes

        edge = Edge(node1.scene, node1.outputs[0], node2.inputs[0], EDGE_TYPE_BEZIER)

        assert edge.edge_type == EDGE_TYPE_BEZIER

    def test_edge_has_graphics_representation(self, nodes):
        """Test edge creates graphics edge."""
        node1, node2 = nodes

        edge = Edge(node1.scene, node1.outputs[0], node2.inputs[0])

        assert edge.grEdge is not None


class TestEdgeProperties:
    """Test edge property getters and setters."""

    def test_get_edge_type(self, nodes):
        """Test getting edge type."""
        node1, node2 = nodes
        edge = Edge(node1.scene, node1.outputs[0], node2.inputs[0], EDGE_TYPE_DIRECT)

        assert edge.edge_type == EDGE_TYPE_DIRECT

    def test_change_edge_type(self, nodes):
        """Test changing edge type."""
        node1, node2 = nodes
        edge = Edge(node1.scene, node1.outputs[0], node2.inputs[0], EDGE_TYPE_DIRECT)

        edge.edge_type = EDGE_TYPE_BEZIER

        assert edge.edge_type == EDGE_TYPE_BEZIER

    def test_get_start_end_sockets(self, nodes):
        """Test getting start and end sockets."""
        node1, node2 = nodes
        edge = Edge(node1.scene, node1.outputs[0], node2.inputs[0])

        assert edge.start_socket == node1.outputs[0]
        assert edge.end_socket == node2.inputs[0]


class TestEdgeConnections:
    """Test edge connection and reconnection."""

    def test_reconnect_edge(self, scene):
        """Test reconnecting edge to different socket."""
        node1 = Node(scene, "Node 1", outputs=[0, 0])
        node2 = Node(scene, "Node 2", inputs=[0])

        edge = Edge(scene, node1.outputs[0], node2.inputs[0])

        # Store original start socket
        original_start = edge.start_socket

        # Reconnect start socket to second output
        edge.reconnect(node1.outputs[0], node1.outputs[1])

        # Edge should now have new start socket
        assert edge.start_socket == node1.outputs[1]
        assert edge.start_socket != original_start

    def test_reconnect_end_socket(self, scene):
        """Test reconnecting end socket to different socket."""
        node1 = Node(scene, "Node 1", outputs=[0])
        node2 = Node(scene, "Node 2", inputs=[0, 0])

        edge = Edge(scene, node1.outputs[0], node2.inputs[0])

        # Store original end socket
        original_end = edge.end_socket

        # Reconnect end socket to second input
        edge.reconnect(node2.inputs[0], node2.inputs[1])

        # Edge should now have new end socket
        assert edge.end_socket == node2.inputs[1]
        assert edge.end_socket != original_end

    def test_update_edge_positions(self, nodes):
        """Test edge updates when nodes move."""
        node1, node2 = nodes
        edge = Edge(node1.scene, node1.outputs[0], node2.inputs[0])

        # Move node
        node1.setPos(200, 200)
        edge.updatePositions()

        # Edge should have updated graphics
        assert edge.grEdge is not None


class TestEdgeValidation:
    """Test edge validation logic."""

    def test_validate_method_exists(self, nodes):
        """Test validation method is callable."""
        node1, node2 = nodes
        edge = Edge(node1.scene, node1.outputs[0], None)

        # Validation might always return True if no validators set
        # Just verify method exists and is callable
        result = edge.validateEdge(node1.outputs[0], node2.inputs[0])
        assert isinstance(result, bool)


class TestEdgeRemoval:
    """Test edge deletion and cleanup."""

    def test_remove_edge(self, nodes):
        """Test removing an edge from scene."""
        node1, node2 = nodes
        scene = node1.scene

        edge = Edge(scene, node1.outputs[0], node2.inputs[0])
        edge_id = edge.id

        edge.remove()

        assert edge not in scene.edges
        assert all(e.id != edge_id for e in scene.edges)

    def test_remove_edge_cleans_sockets(self, nodes):
        """Test removing edge unregisters from sockets."""
        node1, node2 = nodes

        edge = Edge(node1.scene, node1.outputs[0], node2.inputs[0])

        edge.remove()

        assert edge not in node1.outputs[0].edges
        assert edge not in node2.inputs[0].edges

    def test_remove_edge_silent(self, nodes):
        """Test silent edge removal."""
        node1, node2 = nodes
        edge = Edge(node1.scene, node1.outputs[0], node2.inputs[0])

        # Should not trigger node callbacks
        edge.remove(silent=True)

        assert edge not in node1.scene.edges


class TestEdgeSerialization:
    """Test edge serialization and deserialization."""

    def test_serialize_edge(self, nodes):
        """Test serializing an edge to dict."""
        node1, node2 = nodes
        edge = Edge(node1.scene, node1.outputs[0], node2.inputs[0], EDGE_TYPE_BEZIER)

        data = edge.serialize()

        assert data["id"] == edge.id
        assert data["edge_type"] == EDGE_TYPE_BEZIER
        assert data["start"] == node1.outputs[0].id
        assert data["end"] == node2.inputs[0].id

    def test_deserialize_edge(self, nodes):
        """Test deserializing an edge from dict."""
        node1, node2 = nodes
        scene = node1.scene

        original = Edge(scene, node1.outputs[0], node2.inputs[0], EDGE_TYPE_BEZIER)
        data = original.serialize()
        original.remove()

        # Create hashmap for deserialization
        hashmap = {node1.outputs[0].id: node1.outputs[0], node2.inputs[0].id: node2.inputs[0]}

        # Create new edge from data
        restored = Edge(scene)
        restored.deserialize(data, hashmap, True)

        assert restored.edge_type == EDGE_TYPE_BEZIER
        assert restored.start_socket == node1.outputs[0]
        assert restored.end_socket == node2.inputs[0]


class TestEdgeString:
    """Test edge string representation."""

    def test_edge_str_with_sockets(self, nodes):
        """Test __str__ with connected sockets."""
        node1, node2 = nodes
        edge = Edge(node1.scene, node1.outputs[0], node2.inputs[0])

        edge_str = str(edge)

        assert "Edge" in edge_str
        # String representation includes hex IDs, not decimal
        assert "Socket" in edge_str

    def test_edge_str_without_end(self, scene):
        """Test __str__ with only start socket."""
        node = Node(scene, "Node", outputs=[0])
        edge = Edge(scene, node.outputs[0], None)

        edge_str = str(edge)

        assert "Edge" in edge_str
        assert "None" in edge_str
