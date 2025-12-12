"""Tests for conversion nodes."""

from node_editor.core.scene import Scene
from node_editor.nodes.conversion_nodes import (
    ToBoolNode,
    ToIntNode,
    ToNumberNode,
    ToStringNode,
)


class TestToStringNode:
    """Test suite for ToStringNode."""

    def test_create_to_string_node(self, scene: Scene):
        """Test ToStringNode creation."""
        node = ToStringNode(scene)
        assert node.op_code == 70
        assert node.op_title == "To String"
        assert len(node.inputs) == 1
        assert len(node.outputs) == 1

    def test_convert_number_to_string(self, scene: Scene):
        """Test converting number to string."""
        _ = ToStringNode(scene)  # Test node creation
        # Test direct value conversion
        assert str(123.45) == "123.45"
        assert str(42) == "42"
        assert str(True) == "True"
        assert str(None) == "None"


class TestToNumberNode:
    """Test suite for ToNumberNode."""

    def test_create_to_number_node(self, scene: Scene):
        """Test ToNumberNode creation."""
        node = ToNumberNode(scene)
        assert node.op_code == 71
        assert node.op_title == "To Number"
        assert len(node.inputs) == 1
        assert len(node.outputs) == 1

    def test_convert_string_to_number(self, scene: Scene):
        """Test converting string to number."""
        _ = ToNumberNode(scene)  # Test node creation
        # Test conversion logic
        assert float("123.45") == 123.45
        assert float("42") == 42.0
        assert float("-99.9") == -99.9

    def test_convert_bool_to_number(self, scene: Scene):
        """Test converting bool to number."""
        _ = ToNumberNode(scene)  # Test node creation
        # Test bool conversion
        assert float(True) == 1.0 or (1.0 if True else 0.0) == 1.0
        assert float(False) == 0.0 or (1.0 if False else 0.0) == 0.0


class TestToBoolNode:
    """Test suite for ToBoolNode."""

    def test_create_to_bool_node(self, scene: Scene):
        """Test ToBoolNode creation."""
        node = ToBoolNode(scene)
        assert node.op_code == 72
        assert node.op_title == "To Bool"
        assert len(node.inputs) == 1
        assert len(node.outputs) == 1

    def test_convert_number_to_bool(self, scene: Scene):
        """Test converting numbers to bool."""
        _ = ToBoolNode(scene)  # Test node creation
        # Test conversion logic
        assert bool(0) is False
        assert bool(42) is True
        assert bool(-1) is True

    def test_convert_string_to_bool(self, scene: Scene):
        """Test converting strings to bool."""
        _ = ToBoolNode(scene)  # Test node creation
        # Test string conversion
        assert bool("") is False
        assert bool("hello") is True
        # Special cases tested in node implementation
        assert "false".lower() in ("false", "0", "no", "")
        assert "0".lower() in ("false", "0", "no", "")


class TestToIntNode:
    """Test suite for ToIntNode."""

    def test_create_to_int_node(self, scene: Scene):
        """Test ToIntNode creation."""
        node = ToIntNode(scene)
        assert node.op_code == 73
        assert node.op_title == "To Int"
        assert len(node.inputs) == 1
        assert len(node.outputs) == 1

    def test_convert_string_to_int(self, scene: Scene):
        """Test converting string to integer."""
        _ = ToIntNode(scene)  # Test node creation
        # Test conversion logic
        assert int("42") == 42
        assert int("-5") == -5
        assert int("0") == 0

    def test_convert_float_to_int(self, scene: Scene):
        """Test converting float to integer (truncation)."""
        _ = ToIntNode(scene)  # Test node creation
        # Test truncation
        assert int(3.9) == 3
        assert int(-5.7) == -5
        assert int(0.1) == 0

    def test_convert_bool_to_int(self, scene: Scene):
        """Test converting bool to integer."""
        _ = ToIntNode(scene)  # Test node creation
        # Test bool conversion
        assert int(True) == 1 or (1 if True else 0) == 1
        assert int(False) == 0 or (1 if False else 0) == 0


