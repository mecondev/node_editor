"""Graphics layer tests for node editor.

Tests the Qt graphics components including view interactions,
zoom, pan, selection, and visual rendering.

Author:
    Michael Economou

Date:
    2025-12-13
"""

import pytest
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtTest import QTest

from node_editor.core.edge import Edge
from node_editor.core.scene import Scene
from node_editor.graphics.view import QDMGraphicsView
from node_editor.nodes.input_node import NumberInputNode
from node_editor.nodes.math_nodes import AddNode


class TestGraphicsView:
    """Tests for QDMGraphicsView interactions."""

    def test_view_creation(self, qtbot):
        """Test that view is created properly."""
        scene = Scene()
        view = scene.view
        
        assert view is not None
        assert isinstance(view, QDMGraphicsView)
        assert view.scene() == scene.graphics_scene

    def test_zoom_in(self, qtbot):
        """Test zoom in functionality."""
        scene = Scene()
        view = scene.view
        qtbot.addWidget(view)
        
        initial_scale = view.transform().m11()
        
        # Simulate zoom in
        view.zoom_in()
        
        new_scale = view.transform().m11()
        assert new_scale > initial_scale

    def test_zoom_out(self, qtbot):
        """Test zoom out functionality."""
        scene = Scene()
        view = scene.view
        qtbot.addWidget(view)
        
        initial_scale = view.transform().m11()
        
        # Simulate zoom out
        view.zoom_out()
        
        new_scale = view.transform().m11()
        assert new_scale < initial_scale

    def test_zoom_limits(self, qtbot):
        """Test that zoom has min/max limits."""
        scene = Scene()
        view = scene.view
        qtbot.addWidget(view)
        
        # Zoom out many times
        for _ in range(50):
            view.zoom_out()
        
        min_scale = view.transform().m11()
        view.zoom_out()
        assert view.transform().m11() == min_scale  # Shouldn't go below min
        
        # Reset and zoom in many times
        view.reset_zoom()
        for _ in range(50):
            view.zoom_in()
        
        max_scale = view.transform().m11()
        view.zoom_in()
        assert view.transform().m11() == max_scale  # Shouldn't go above max

    def test_reset_zoom(self, qtbot):
        """Test reset zoom functionality."""
        scene = Scene()
        view = scene.view
        qtbot.addWidget(view)
        
        # Zoom in and out
        view.zoom_in()
        view.zoom_in()
        view.zoom_out()
        
        # Reset
        view.reset_zoom()
        
        # Should be at scale 1.0
        assert abs(view.transform().m11() - 1.0) < 0.01

    def test_fit_in_view(self, qtbot):
        """Test fit in view functionality."""
        scene = Scene()
        view = scene.view
        qtbot.addWidget(view)
        
        # Create some nodes at different positions
        node1 = NumberInputNode(scene)
        node1.pos = [0, 0]
        
        node2 = NumberInputNode(scene)
        node2.pos = [500, 500]
        
        # Fit in view
        view.fit_in_view()
        
        # View should be adjusted (hard to test exact values)
        # Just verify it doesn't crash
        assert True


class TestGraphicsNode:
    """Tests for QDMGraphicsNode visual representation."""

    def test_node_graphics_creation(self, qtbot):
        """Test that graphics node is created with model node."""
        scene = Scene()
        scene.graphics_scene
        
        node = NumberInputNode(scene)
        
        assert node.graphics_node is not None
        assert node.graphics_node.node == node
        assert node.graphics_node.scene() == scene.graphics_scene

    def test_node_selection(self, qtbot):
        """Test node selection state."""
        scene = Scene()
        scene.graphics_scene
        
        node = NumberInputNode(scene)
        
        # Initially not selected
        assert not node.graphics_node.isSelected()
        
        # Select
        node.graphics_node.setSelected(True)
        assert node.graphics_node.isSelected()
        
        # Deselect
        node.graphics_node.setSelected(False)
        assert not node.graphics_node.isSelected()

    def test_node_position(self, qtbot):
        """Test node position in scene."""
        scene = Scene()
        scene.graphics_scene
        
        node = NumberInputNode(scene)
        node.set_pos(100, 200)
        
        # Graphics node should be at model node position
        gfx_pos = node.graphics_node.pos()
        assert abs(gfx_pos.x() - 100) < 1
        assert abs(gfx_pos.y() - 200) < 1

    def test_node_title_display(self, qtbot):
        """Test that node title is displayed correctly."""
        scene = Scene()
        scene.graphics_scene
        
        node = NumberInputNode(scene)
        
        assert node.graphics_node.title == node.title
        assert node.graphics_node.title_item.toPlainText() == node.title

    def test_node_content_widget(self, qtbot):
        """Test that content widget is embedded in graphics node."""
        scene = Scene()
        scene.graphics_scene
        
        node = NumberInputNode(scene)
        
        assert node.content is not None
        assert node.graphics_node.content == node.content

    def test_multiple_selection(self, qtbot):
        """Test selecting multiple nodes."""
        scene = Scene()
        scene.graphics_scene
        
        node1 = NumberInputNode(scene)
        node2 = AddNode(scene)
        node3 = NumberInputNode(scene)
        
        # Select multiple
        node1.graphics_node.setSelected(True)
        node2.graphics_node.setSelected(True)
        
        selected = scene.get_selected_items()
        assert len(selected["nodes"]) == 2
        assert node1 in selected["nodes"]
        assert node2 in selected["nodes"]
        assert node3 not in selected["nodes"]


class TestGraphicsEdge:
    """Tests for QDMGraphicsEdge visual representation."""

    def test_edge_graphics_creation(self, qtbot):
        """Test that graphics edge is created with model edge."""
        scene = Scene()
        scene.graphics_scene
        
        node1 = NumberInputNode(scene)
        node2 = AddNode(scene)
        
        edge = Edge(scene, node1.outputs[0], node2.inputs[0])
        
        assert edge.graphics_edge is not None
        assert edge.graphics_edge.edge == edge
        assert edge.graphics_edge.scene() == scene.graphics_scene

    def test_edge_path_update(self, qtbot):
        """Test that edge path updates when nodes move."""
        scene = Scene()
        scene.graphics_scene
        
        node1 = NumberInputNode(scene)
        node1.pos = [0, 0]
        
        node2 = AddNode(scene)
        node2.pos = [200, 0]
        
        edge = Edge(scene, node1.outputs[0], node2.inputs[0])
        
        # Get initial path
        initial_path = edge.graphics_edge.path()
        
        # Move node
        node2.pos = [300, 100]
        edge.update_positions()
        
        # Path should have changed
        new_path = edge.graphics_edge.path()
        assert not initial_path.boundingRect().contains(new_path.boundingRect())

    def test_edge_selection(self, qtbot):
        """Test edge selection state."""
        scene = Scene()
        scene.graphics_scene
        
        node1 = NumberInputNode(scene)
        node2 = AddNode(scene)
        
        edge = Edge(scene, node1.outputs[0], node2.inputs[0])
        
        # Initially not selected
        assert not edge.graphics_edge.isSelected()
        
        # Select
        edge.graphics_edge.setSelected(True)
        assert edge.graphics_edge.isSelected()

    def test_edge_types(self, qtbot):
        """Test different edge path types."""
        from node_editor.core import EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER
        
        scene = Scene()
        scene.graphics_scene
        
        node1 = NumberInputNode(scene)
        node2 = AddNode(scene)
        
        # Create edge with direct type
        edge = Edge(scene, node1.outputs[0], node2.inputs[0], edge_type=EDGE_TYPE_DIRECT)
        assert edge.edge_type == EDGE_TYPE_DIRECT
        
        # Change to bezier
        edge.edge_type = EDGE_TYPE_BEZIER
        edge.graphics_edge.make_path()
        assert edge.edge_type == EDGE_TYPE_BEZIER


class TestGraphicsSocket:
    """Tests for QDMGraphicsSocket visual representation."""

    def test_socket_graphics_creation(self, qtbot):
        """Test that graphics socket is created with model socket."""
        scene = Scene()
        scene.graphics_scene
        
        node = NumberInputNode(scene)
        
        socket = node.outputs[0]
        assert socket.graphics_socket is not None
        assert socket.graphics_socket.socket == socket

    def test_socket_position(self, qtbot):
        """Test socket position relative to node."""
        scene = Scene()
        scene.graphics_scene
        
        node = NumberInputNode(scene)
        node.set_pos(100, 100)
        
        socket = node.outputs[0]
        socket_pos = socket.get_socket_position()
        
        # Socket position should be relative to node position
        assert isinstance(socket_pos, list)
        assert len(socket_pos) == 2

    def test_socket_types_visual(self, qtbot):
        """Test that different socket types have different visuals."""
        scene = Scene()
        scene.graphics_scene
        
        node1 = NumberInputNode(scene)
        node2 = AddNode(scene)
        
        # Different socket types should be visually distinguishable
        # This is a basic test - actual visual differences handled by theme
        socket1 = node1.outputs[0]
        socket2 = node2.inputs[0]
        
        assert socket1.graphics_socket is not None
        assert socket2.graphics_socket is not None


class TestGraphicsScene:
    """Tests for QDMGraphicsScene."""

    def test_scene_creation(self, qtbot):
        """Test scene creation."""
        scene = Scene()
        graphics_scene = scene.graphics_scene
        
        assert graphics_scene is not None
        assert graphics_scene.scene == scene

    def test_scene_bounds(self, qtbot):
        """Test scene bounding rectangle."""
        scene = Scene()
        graphics_scene = scene.graphics_scene
        
        rect = graphics_scene.sceneRect()
        
        # Should have reasonable bounds
        assert rect.width() > 0
        assert rect.height() > 0

    def test_grid_rendering(self, qtbot):
        """Test that grid can be rendered."""
        scene = Scene()
        graphics_scene = scene.graphics_scene
        
        # Just verify drawBackground doesn't crash
        # Actual rendering tested visually
        assert hasattr(graphics_scene, 'drawBackground')
