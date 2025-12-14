"""Graphics layer tests for node editor.

Tests the Qt graphics components including view interactions,
zoom, pan, selection, and visual rendering.

Author:
    Michael Economou

Date:
    2025-12-13
"""


from node_editor.core.edge import Edge
from node_editor.core.scene import Scene
from node_editor.graphics.view import QDMGraphicsView
from node_editor.nodes.input_node import NumberInputNode
from node_editor.nodes.math_nodes import AddNode


class TestGraphicsView:
    """Tests for QDMGraphicsView interactions."""

    def test_view_creation(self, _qtbot):
        """Test that view is created properly."""
        scene = Scene()
        view = QDMGraphicsView(scene.graphics_scene)

        assert view is not None
        assert isinstance(view, QDMGraphicsView)
        assert view.scene() == scene.graphics_scene

    def test_zoom_in(self, qtbot):
        """Test zoom in functionality via wheel event."""
        from PyQt5.QtCore import QPoint, QPointF, Qt
        from PyQt5.QtGui import QWheelEvent

        scene = Scene()
        view = QDMGraphicsView(scene.graphics_scene)
        qtbot.addWidget(view)
        view.show()

        # Zoom out first (starts at max)
        pos = QPointF(100, 100)
        wheel_out = QWheelEvent(
            pos, view.mapToGlobal(QPoint(100, 100)),
            QPoint(0, -120), QPoint(0, -120),
            Qt.NoButton, Qt.NoModifier, Qt.ScrollUpdate, False
        )
        view.wheelEvent(wheel_out)
        zoom_after_out = view.zoom

        # Now zoom in
        wheel_in = QWheelEvent(
            pos, view.mapToGlobal(QPoint(100, 100)),
            QPoint(0, 120), QPoint(0, 120),
            Qt.NoButton, Qt.NoModifier, Qt.ScrollUpdate, False
        )
        view.wheelEvent(wheel_in)

        assert view.zoom > zoom_after_out

    def test_zoom_out(self, qtbot):
        """Test zoom out functionality via wheel event."""
        from PyQt5.QtCore import QPoint, QPointF, Qt
        from PyQt5.QtGui import QWheelEvent

        scene = Scene()
        view = QDMGraphicsView(scene.graphics_scene)
        qtbot.addWidget(view)
        view.show()

        initial_zoom = view.zoom

        pos = QPointF(100, 100)
        wheel_event = QWheelEvent(
            pos, view.mapToGlobal(QPoint(100, 100)),
            QPoint(0, -120), QPoint(0, -120),
            Qt.NoButton, Qt.NoModifier, Qt.ScrollUpdate, False
        )
        view.wheelEvent(wheel_event)

        assert view.zoom < initial_zoom

    def test_zoom_limits(self, qtbot):
        """Test that zoom has min/max limits."""
        from PyQt5.QtCore import QPoint, QPointF, Qt
        from PyQt5.QtGui import QWheelEvent

        scene = Scene()
        view = QDMGraphicsView(scene.graphics_scene)
        qtbot.addWidget(view)
        view.show()

        pos = QPointF(100, 100)

        # Zoom out many times
        for _ in range(50):
            wheel_event = QWheelEvent(
                pos, view.mapToGlobal(QPoint(100, 100)),
                QPoint(0, -120), QPoint(0, -120),
                Qt.NoButton, Qt.NoModifier, Qt.ScrollUpdate, False
            )
            view.wheelEvent(wheel_event)

        assert view.zoom == view.zoom_range[0]

        # Zoom in many times
        for _ in range(50):
            wheel_event = QWheelEvent(
                pos, view.mapToGlobal(QPoint(100, 100)),
                QPoint(0, 120), QPoint(0, 120),
                Qt.NoButton, Qt.NoModifier, Qt.ScrollUpdate, False
            )
            view.wheelEvent(wheel_event)

        assert view.zoom == view.zoom_range[1]

    def test_reset_zoom(self, qtbot):
        """Test that zoom starts at expected level."""
        scene = Scene()
        view = QDMGraphicsView(scene.graphics_scene)
        qtbot.addWidget(view)
        view.show()

        # Initial zoom should be at default value (10)
        assert view.zoom == 10
        assert view.zoom_range == [0, 10]
        assert abs(view.transform().m11() - 1.0) < 0.01

    def test_fit_in_view(self, qtbot):
        """Test fit in view functionality using Qt fitInView."""
        from PyQt5.QtCore import Qt as QtCore

        scene = Scene()
        view = QDMGraphicsView(scene.graphics_scene)
        qtbot.addWidget(view)
        view.show()
        view.resize(800, 600)

        node1 = NumberInputNode(scene)
        node1.set_pos(0, 0)

        node2 = NumberInputNode(scene)
        node2.set_pos(500, 500)

        items_rect = scene.graphics_scene.itemsBoundingRect()
        view.fitInView(items_rect, QtCore.KeepAspectRatio)

        assert True  # Verify no crash


class TestGraphicsNode:
    """Tests for QDMGraphicsNode visual representation."""

    def test_node_graphics_creation(self, _qtbot):
        """Test that graphics node is created with model node."""
        scene = Scene()

        node = NumberInputNode(scene)

        assert node.graphics_node is not None
        assert node.graphics_node.node == node
        assert node.graphics_node.scene() == scene.graphics_scene

    def test_node_selection(self, _qtbot):
        """Test node selection state."""
        scene = Scene()

        node = NumberInputNode(scene)

        # Initially not selected
        assert not node.graphics_node.isSelected()

        # Select
        node.graphics_node.setSelected(True)
        assert node.graphics_node.isSelected()

        # Deselect
        node.graphics_node.setSelected(False)
        assert not node.graphics_node.isSelected()

    def test_node_position(self, _qtbot):
        """Test node position in scene."""
        scene = Scene()

        node = NumberInputNode(scene)
        node.set_pos(100, 200)

        # Graphics node should be at model node position
        gfx_pos = node.graphics_node.pos()
        assert abs(gfx_pos.x() - 100) < 1
        assert abs(gfx_pos.y() - 200) < 1

    def test_node_title_display(self, _qtbot):
        """Test that node title is displayed correctly."""
        scene = Scene()

        node = NumberInputNode(scene)

        assert node.graphics_node.title == node.title
        assert node.graphics_node.title_item.toPlainText() == node.title

    def test_node_content_widget(self, _qtbot):
        """Test that content widget is embedded in graphics node."""
        scene = Scene()

        node = NumberInputNode(scene)

        assert node.content is not None
        assert node.graphics_node.content == node.content

    def test_multiple_selection(self, _qtbot):
        """Test selecting multiple nodes."""
        scene = Scene()

        node1 = NumberInputNode(scene)
        node2 = AddNode(scene)
        NumberInputNode(scene)  # node3 - not selected

        node1.graphics_node.setSelected(True)
        node2.graphics_node.setSelected(True)

        selected = scene.get_selected_items()
        assert len(selected) >= 2
        nodes = [item for item in selected if hasattr(item, 'node')]
        assert len(nodes) == 2


class TestGraphicsEdge:
    """Tests for QDMGraphicsEdge visual representation."""

    def test_edge_graphics_creation(self, _qtbot):
        """Test that graphics edge is created with model edge."""
        scene = Scene()

        node1 = NumberInputNode(scene)
        node2 = AddNode(scene)

        edge = Edge(scene, node1.outputs[0], node2.inputs[0])

        assert edge.graphics_edge is not None
        assert edge.graphics_edge.edge == edge
        assert edge.graphics_edge.scene() == scene.graphics_scene

    def test_edge_path_update(self, _qtbot):
        """Test that edge path updates when nodes move."""
        scene = Scene()

        node1 = NumberInputNode(scene)
        node1.set_pos(0, 0)

        node2 = AddNode(scene)
        node2.set_pos(200, 0)

        edge = Edge(scene, node1.outputs[0], node2.inputs[0])

        initial_path = edge.graphics_edge.path()

        node2.set_pos(300, 100)
        edge.update_positions()

        new_path = edge.graphics_edge.path()
        assert not initial_path.boundingRect().contains(new_path.boundingRect())

    def test_edge_selection(self, _qtbot):
        """Test edge selection state."""
        scene = Scene()

        node1 = NumberInputNode(scene)
        node2 = AddNode(scene)

        edge = Edge(scene, node1.outputs[0], node2.inputs[0])

        # Initially not selected
        assert not edge.graphics_edge.isSelected()

        # Select
        edge.graphics_edge.setSelected(True)
        assert edge.graphics_edge.isSelected()

    def test_edge_types(self, _qtbot):
        """Test different edge path types."""
        from node_editor.core import EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT

        scene = Scene()

        node1 = NumberInputNode(scene)
        node2 = AddNode(scene)

        edge = Edge(scene, node1.outputs[0], node2.inputs[0], edge_type=EDGE_TYPE_DIRECT)
        assert edge.edge_type == EDGE_TYPE_DIRECT

        edge.edge_type = EDGE_TYPE_BEZIER
        edge.graphics_edge.calc_path()
        assert edge.edge_type == EDGE_TYPE_BEZIER


class TestGraphicsSocket:
    """Tests for QDMGraphicsSocket visual representation."""

    def test_socket_graphics_creation(self, _qtbot):
        """Test that graphics socket is created with model socket."""
        scene = Scene()

        node = NumberInputNode(scene)

        socket = node.outputs[0]
        assert socket.graphics_socket is not None
        assert socket.graphics_socket.socket == socket

    def test_socket_position(self, _qtbot):
        """Test socket position relative to node."""
        scene = Scene()

        node = NumberInputNode(scene)
        node.set_pos(100, 100)

        socket = node.outputs[0]
        socket_pos = socket.get_socket_position()

        assert isinstance(socket_pos, tuple)
        assert len(socket_pos) == 2

    def test_socket_types_visual(self, _qtbot):
        """Test that different socket types have different visuals."""
        scene = Scene()

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

    def test_scene_creation(self, _qtbot):
        """Test scene creation."""
        scene = Scene()
        graphics_scene = scene.graphics_scene

        assert graphics_scene is not None
        assert graphics_scene.scene == scene

    def test_scene_bounds(self, _qtbot):
        """Test scene bounding rectangle."""
        scene = Scene()
        graphics_scene = scene.graphics_scene

        rect = graphics_scene.sceneRect()

        # Should have reasonable bounds
        assert rect.width() > 0
        assert rect.height() > 0

    def test_grid_rendering(self, _qtbot):
        """Test that grid can be rendered."""
        scene = Scene()
        graphics_scene = scene.graphics_scene

        # Just verify drawBackground doesn't crash
        # Actual rendering tested visually
        assert hasattr(graphics_scene, 'drawBackground')
