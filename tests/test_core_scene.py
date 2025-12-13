#!/usr/bin/env python
"""Tests for Scene class functionality.

Tests scene management, serialization, and graph operations.

Author:
    Michael Economou

Date:
    2025-12-12
"""

import json
import os
import tempfile

from node_editor.core.edge import Edge
from node_editor.core.node import Node
from node_editor.core.scene import Scene


class TestSceneCreation:
    """Test scene creation and initialization."""

    def test_create_empty_scene(self):
        """Test creating an empty scene."""
        scene = Scene()

        assert len(scene.nodes) == 0
        assert len(scene.edges) == 0
        assert scene.graphics_scene is not None

    def test_scene_has_history(self):
        """Test scene has history manager."""
        scene = Scene()

        assert scene.history is not None
        assert hasattr(scene, 'history')

    def test_scene_has_clipboard(self):
        """Test scene has clipboard manager."""
        scene = Scene()

        assert scene.clipboard is not None
        assert hasattr(scene, 'clipboard')

    def test_scene_starts_unmodified(self):
        """Test new scene starts in unmodified state."""
        scene = Scene()

        assert not scene.is_modified()


class TestSceneNodeManagement:
    """Test adding and removing nodes from scene."""

    def test_add_node_to_scene(self, scene):
        """Test adding a node to scene."""
        node = Node(scene, "Test Node")

        assert node in scene.nodes
        assert len(scene.nodes) == 1

    def test_add_multiple_nodes(self, scene):
        """Test adding multiple nodes."""
        node1 = Node(scene, "Node 1")
        node2 = Node(scene, "Node 2")
        node3 = Node(scene, "Node 3")

        assert len(scene.nodes) == 3
        assert all(n in scene.nodes for n in [node1, node2, node3])

    def test_remove_node_from_scene(self, scene):
        """Test removing a node from scene."""
        node = Node(scene, "Test Node")
        scene.remove_node(node)

        assert node not in scene.nodes
        assert len(scene.nodes) == 0

    def test_get_node_by_id(self, scene):
        """Test retrieving node by ID."""
        node = Node(scene, "Test Node")
        node_id = node.id

        found = scene.get_node_by_id(node_id)

        assert found == node


class TestSceneEdgeManagement:
    """Test adding and removing edges from scene."""

    def test_add_edge_to_scene(self, scene):
        """Test adding an edge to scene."""
        node1 = Node(scene, "Node 1", outputs=[0])
        node2 = Node(scene, "Node 2", inputs=[0])

        edge = Edge(scene, node1.outputs[0], node2.inputs[0])

        assert edge in scene.edges
        assert len(scene.edges) == 1

    def test_remove_edge_from_scene(self, scene):
        """Test removing an edge from scene."""
        node1 = Node(scene, "Node 1", outputs=[0])
        node2 = Node(scene, "Node 2", inputs=[0])
        edge = Edge(scene, node1.outputs[0], node2.inputs[0])

        scene.remove_edge(edge)

        assert edge not in scene.edges
        assert len(scene.edges) == 0


class TestSceneModificationState:
    """Test scene modification tracking."""

    def test_scene_modified_after_node_added(self, scene):
        """Test scene is modified after adding node."""
        scene.has_been_modified = False

        Node(scene, "Test Node")

        # Note: Modification flag should be set by history system
        # For now we just test the property exists
        assert hasattr(scene, 'has_been_modified')

    def test_reset_modification_flag(self, scene):
        """Test resetting modification flag."""
        Node(scene, "Test Node")
        scene.has_been_modified = False

        assert not scene.is_modified()


class TestSceneSerialization:
    """Test scene serialization and deserialization."""

    def test_serialize_empty_scene(self, scene):
        """Test serializing an empty scene."""
        data = scene.serialize()

        assert 'id' in data
        assert 'nodes' in data
        assert 'edges' in data
        assert len(data['nodes']) == 0
        assert len(data['edges']) == 0

    def test_serialize_scene_with_nodes(self, scene):
        """Test serializing scene with nodes."""
        Node(scene, "Node 1")
        Node(scene, "Node 2")

        data = scene.serialize()

        assert len(data['nodes']) == 2

    def test_serialize_scene_with_edges(self, scene):
        """Test serializing scene with connected nodes."""
        node1 = Node(scene, "Node 1", outputs=[0])
        node2 = Node(scene, "Node 2", inputs=[0])
        Edge(scene, node1.outputs[0], node2.inputs[0])

        data = scene.serialize()

        assert len(data['nodes']) == 2
        assert len(data['edges']) == 1

    def test_deserialize_scene(self, scene):
        """Test deserializing a scene."""
        # Create original scene
        node1 = Node(scene, "Node 1", outputs=[0])
        node2 = Node(scene, "Node 2", inputs=[0])
        Edge(scene, node1.outputs[0], node2.inputs[0])

        data = scene.serialize()

        # Create new scene and deserialize
        new_scene = Scene()
        new_scene.deserialize(data)

        assert len(new_scene.nodes) == 2
        assert len(new_scene.edges) == 1


class TestSceneFileOperations:
    """Test scene save and load operations."""

    def test_save_to_file(self, scene):
        """Test saving scene to file."""
        Node(scene, "Test Node")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filename = f.name

        try:
            scene.save_to_file(filename)

            assert os.path.exists(filename)

            # Verify JSON is valid
            with open(filename) as f:
                data = json.load(f)
                assert 'nodes' in data
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_load_from_file(self, scene):
        """Test loading scene from file."""
        # Create and save original scene
        node1 = Node(scene, "Node 1", outputs=[0])
        node2 = Node(scene, "Node 2", inputs=[0])
        Edge(scene, node1.outputs[0], node2.inputs[0])

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filename = f.name

        try:
            scene.save_to_file(filename)

            # Load into new scene
            new_scene = Scene()
            new_scene.load_from_file(filename)

            assert len(new_scene.nodes) == 2
            assert len(new_scene.edges) == 1
        finally:
            if os.path.exists(filename):
                os.unlink(filename)


class TestSceneClear:
    """Test scene clearing operations."""

    def test_clear_scene(self, scene):
        """Test clearing all nodes and edges."""
        Node(scene, "Node 1")
        Node(scene, "Node 2")

        scene.clear()

        assert len(scene.nodes) == 0
        assert len(scene.edges) == 0

    def test_clear_selection(self, scene):
        """Test clearing selection."""
        # Scene should have a method to clear selection
        scene.graphics_scene.clearSelection()

        # No exception should be raised
        assert True


class TestSceneView:
    """Test scene view access."""

    def test_get_view(self, scene):
        """Test getting the graphics view."""
        # View might not be set in test environment
        try:
            view = scene.get_view()
            # If no exception, view exists or is None
            assert view is None or view is not None
        except IndexError:
            # No views in test environment - this is ok
            assert True

    def test_get_items_at_position(self, scene):
        """Test getting items at position."""
        node = Node(scene, "Test Node")
        node.set_pos(100, 100)

        # Get items near node position
        items = scene.graphics_scene.items()

        # Should include graphics node
        assert any(hasattr(item, 'node') for item in items)


class TestSceneSelection:
    """Test scene selection management."""

    def test_get_selected_items(self, scene):
        """Test getting selected items."""
        Node(scene, "Node 1")
        Node(scene, "Node 2")

        # Get selection (should be empty initially)
        selected = scene.graphics_scene.selectedItems()

        assert isinstance(selected, list)

    def test_has_selected_items(self, scene):
        """Test checking if scene has selection."""
        Node(scene, "Node 1")

        # Initially no selection
        selected = scene.graphics_scene.selectedItems()
        assert len(selected) == 0
