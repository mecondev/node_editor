#!/usr/bin/env python
"""Basic import tests for the node_editor package.

Verifies that core module imports work correctly and essential
classes are properly initialized.

Author:
    Michael Economou

Date:
    2025-12-11
"""


import unittest


class TestPackageImports(unittest.TestCase):
    """Basic tests for node_editor package imports."""

    def test_core_imports(self):
        """Test that core modules can be imported."""
        from node_editor.core.edge import Edge
        from node_editor.core.node import Node
        from node_editor.core.scene import Scene
        from node_editor.core.socket import Socket

        assert Edge is not None
        assert Node is not None
        assert Scene is not None
        assert Socket is not None

    def test_graphics_imports(self):
        """Test that graphics modules can be imported."""
        from node_editor.graphics.edge import QDMGraphicsEdge
        from node_editor.graphics.node import QDMGraphicsNode
        from node_editor.graphics.scene import QDMGraphicsScene
        from node_editor.graphics.socket import QDMGraphicsSocket
        from node_editor.graphics.view import QDMGraphicsView

        assert QDMGraphicsEdge is not None
        assert QDMGraphicsNode is not None
        assert QDMGraphicsScene is not None
        assert QDMGraphicsSocket is not None
        assert QDMGraphicsView is not None

    def test_widget_imports(self):
        """Test that widget modules can be imported."""
        from node_editor.widgets.content_widget import QDMNodeContentWidget
        from node_editor.widgets.editor_widget import NodeEditorWidget
        from node_editor.widgets.editor_window import NodeEditorWindow

        assert QDMNodeContentWidget is not None
        assert NodeEditorWidget is not None
        assert NodeEditorWindow is not None

    def test_tools_imports(self):
        """Test that tool modules can be imported."""
        from node_editor.tools.edge_dragging import EdgeDragging
        from node_editor.tools.edge_intersect import EdgeIntersect
        from node_editor.tools.edge_rerouting import EdgeRerouting
        from node_editor.tools.edge_snapping import EdgeSnapping
        from node_editor.tools.edge_validators import (
            edge_cannot_connect_input_and_output_of_different_type,
            edge_cannot_connect_input_and_output_of_same_node,
            edge_cannot_connect_two_outputs_or_two_inputs,
        )

        assert EdgeDragging is not None
        assert EdgeIntersect is not None
        assert EdgeRerouting is not None
        assert EdgeSnapping is not None
        assert edge_cannot_connect_two_outputs_or_two_inputs is not None
        assert edge_cannot_connect_input_and_output_of_same_node is not None
        assert edge_cannot_connect_input_and_output_of_different_type is not None

    def test_utils_imports(self):
        """Test that utility modules can be imported."""
        from node_editor.utils.helpers import dump_exception, pp
        from node_editor.utils.logging_config import setup_logging
        from node_editor.utils.qt_helpers import is_ctrl_pressed, is_shift_pressed

        assert dump_exception is not None
        assert pp is not None
        assert setup_logging is not None
        assert is_ctrl_pressed is not None
        assert is_shift_pressed is not None

    def test_scene_has_required_attributes(self):
        """Test if Scene class has essential attributes and methods."""
        from node_editor.core.scene import Scene

        # Test class attributes/methods exist (no instantiation needed)
        assert hasattr(Scene, "has_been_modified")
        assert hasattr(Scene, "__init__")
        assert hasattr(Scene, "add_node")
        assert hasattr(Scene, "add_edge")
        assert hasattr(Scene, "clear")
        assert hasattr(Scene, "serialize")
        assert hasattr(Scene, "deserialize")

    def test_node_class_attributes(self):
        """Test Node class has essential attributes."""
        from node_editor.core.node import Node

        # Test class attributes exist (no instantiation to avoid QApplication requirement)
        assert hasattr(Node, "__init__")
        assert hasattr(Node, "mark_dirty")
        assert hasattr(Node, "mark_invalid")
        assert hasattr(Node, "eval")
        assert hasattr(Node, "serialize")
        assert hasattr(Node, "deserialize")
