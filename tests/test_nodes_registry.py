"""Tests for NodeRegistry.

Tests node registration, duplicate detection, and lookup functionality.
"""

import pytest

from node_editor.core.node import Node
from node_editor.core.scene import Scene
from node_editor.nodes.registry import NodeRegistry


class TestNodeRegistry:
    """Test suite for NodeRegistry class."""

    def test_register_decorator_success(self, qtbot):
        """Test successful node registration using decorator."""
        # Create a unique op_code for this test
        test_op_code = 9999

        # Clean up if exists from previous test run
        if test_op_code in NodeRegistry._nodes:
            del NodeRegistry._nodes[test_op_code]

        @NodeRegistry.register(test_op_code)
        class TestNode(Node):
            def __init__(self, scene):
                super().__init__(scene, "Test Node")

        # Verify registration
        assert test_op_code in NodeRegistry._nodes
        assert NodeRegistry._nodes[test_op_code] == TestNode
        assert TestNode.op_code == test_op_code

        # Clean up
        del NodeRegistry._nodes[test_op_code]

    def test_register_duplicate_op_code_raises_error(self, qtbot):
        """Test that registering duplicate op_code raises ValueError."""
        test_op_code = 9998

        # Clean up if exists
        if test_op_code in NodeRegistry._nodes:
            del NodeRegistry._nodes[test_op_code]

        @NodeRegistry.register(test_op_code)
        class FirstNode(Node):
            def __init__(self, scene):
                super().__init__(scene, "First Node")

        # Attempting to register another node with same op_code should raise
        with pytest.raises(ValueError, match=f"OpCode {test_op_code} already registered"):
            @NodeRegistry.register(test_op_code)
            class SecondNode(Node):
                def __init__(self, scene):
                    super().__init__(scene, "Second Node")

        # Clean up
        del NodeRegistry._nodes[test_op_code]

    def test_register_node_method_success(self, qtbot):
        """Test successful node registration using register_node method."""
        test_op_code = 9997

        # Clean up if exists
        if test_op_code in NodeRegistry._nodes:
            del NodeRegistry._nodes[test_op_code]

        class TestNode(Node):
            def __init__(self, scene):
                super().__init__(scene, "Test Node")

        NodeRegistry.register_node(test_op_code, TestNode)

        # Verify registration
        assert test_op_code in NodeRegistry._nodes
        assert NodeRegistry._nodes[test_op_code] == TestNode
        assert TestNode.op_code == test_op_code

        # Clean up
        del NodeRegistry._nodes[test_op_code]

    def test_register_node_method_duplicate_raises_error(self, qtbot):
        """Test that register_node raises ValueError for duplicate op_code."""
        test_op_code = 9996

        # Clean up if exists
        if test_op_code in NodeRegistry._nodes:
            del NodeRegistry._nodes[test_op_code]

        class FirstNode(Node):
            def __init__(self, scene):
                super().__init__(scene, "First Node")

        class SecondNode(Node):
            def __init__(self, scene):
                super().__init__(scene, "Second Node")

        NodeRegistry.register_node(test_op_code, FirstNode)

        # Attempting to register another node should raise
        with pytest.raises(ValueError, match=f"OpCode {test_op_code} already registered"):
            NodeRegistry.register_node(test_op_code, SecondNode)

        # Clean up
        del NodeRegistry._nodes[test_op_code]

    def test_get_node_class_existing(self, qtbot):
        """Test getting an existing node class."""
        test_op_code = 9995

        # Clean up if exists
        if test_op_code in NodeRegistry._nodes:
            del NodeRegistry._nodes[test_op_code]

        @NodeRegistry.register(test_op_code)
        class TestNode(Node):
            def __init__(self, scene):
                super().__init__(scene, "Test Node")

        # Retrieve the node class
        retrieved_class = NodeRegistry.get_node_class(test_op_code)
        assert retrieved_class == TestNode

        # Clean up
        del NodeRegistry._nodes[test_op_code]

    def test_get_node_class_nonexistent(self, qtbot):
        """Test getting a non-existent node class returns None."""
        nonexistent_op_code = 99999
        retrieved_class = NodeRegistry.get_node_class(nonexistent_op_code)
        assert retrieved_class is None

    def test_get_all_nodes(self, qtbot):
        """Test getting all registered node classes."""
        # This should return a dictionary with at least the built-in nodes
        all_nodes = NodeRegistry.get_all_nodes()
        assert isinstance(all_nodes, dict)
        
        # Check that some built-in nodes are present
        assert 1 in all_nodes  # NumberInputNode
        assert 2 in all_nodes  # TextInputNode
        assert 3 in all_nodes  # OutputNode
        
        # Verify it's a copy, not the internal dict
        original_count = len(all_nodes)
        all_nodes[88888] = None
        all_nodes_again = NodeRegistry.get_all_nodes()
        assert len(all_nodes_again) == original_count

    def test_node_instantiation_after_registration(self, qtbot, scene):
        """Test that a registered node can be instantiated and used."""
        test_op_code = 9994

        # Clean up if exists
        if test_op_code in NodeRegistry._nodes:
            del NodeRegistry._nodes[test_op_code]

        @NodeRegistry.register(test_op_code)
        class TestNode(Node):
            def __init__(self, scene):
                super().__init__(scene, "Test Node", inputs=[1], outputs=[1])

            def eval(self):
                return 42

        # Create instance
        node = TestNode(scene)
        assert node.op_code == test_op_code
        assert node.title == "Test Node"
        assert len(node.inputs) == 1
        assert len(node.outputs) == 1
        assert node.eval() == 42

        # Clean up
        del NodeRegistry._nodes[test_op_code]
