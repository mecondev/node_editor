"""Tests for utility nodes.

Author:
    Michael Economou

Date:
    2025-12-12
"""

from node_editor.core.scene import Scene
from node_editor.nodes.input_node import NumberInputNode
from node_editor.nodes.utility_nodes import (
    ClampNode,
    CommentNode,
    ConstantNode,
    PrintNode,
    RandomNode,
)


class TestConstantNode:
    """Test suite for ConstantNode."""

    def test_create_constant_node(self, scene: Scene):
        """Test creating a constant node."""
        node = ConstantNode(scene)
        assert node is not None
        assert node.op_code == 80
        assert node.op_title == "Constant"
        assert len(node.inputs) == 0
        assert len(node.outputs) == 1

    def test_constant_numeric_value(self, scene: Scene):
        """Test constant with numeric value."""
        node = ConstantNode(scene)
        node.content.edit.setText("42")

        result = node.eval()
        assert result == 42
        assert isinstance(result, int)

    def test_constant_float_value(self, scene: Scene):
        """Test constant with float value."""
        node = ConstantNode(scene)
        node.content.edit.setText("3.14")

        result = node.eval()
        assert result == 3.14
        assert isinstance(result, float)

    def test_constant_string_value(self, scene: Scene):
        """Test constant with string value."""
        node = ConstantNode(scene)
        node.content.edit.setText("hello")

        result = node.eval()
        assert result == "hello"
        assert isinstance(result, str)

    def test_constant_serialization(self, scene: Scene):
        """Test constant node serialization."""
        node = ConstantNode(scene)
        node.content.edit.setText("123")

        data = node.serialize()
        assert "value" in data
        assert data["value"] == "123"

    def test_constant_deserialization(self, scene: Scene):
        """Test constant node deserialization."""
        # Create and serialize a node
        node1 = ConstantNode(scene)
        node1.content.edit.setText("456")
        data = node1.serialize()

        # Create a new node and deserialize
        node2 = ConstantNode(scene)
        node2.deserialize(data, {}, True)
        assert node2.content.edit.text() == "456"


class TestPrintNode:
    """Test suite for PrintNode."""

    def test_create_print_node(self, scene: Scene):
        """Test creating a print node."""
        node = PrintNode(scene)
        assert node is not None
        assert node.op_code == 81
        assert node.op_title == "Print"
        assert len(node.inputs) == 1
        assert len(node.outputs) == 1

    def test_print_passes_through_value(self, scene: Scene):
        """Test print node passes value through."""
        print_node = PrintNode(scene)
        input_node = NumberInputNode(scene)

        input_node.content.edit.setText("42")
        input_node.eval()

        print_node.getInput = lambda idx: input_node if idx == 0 else None

        result = print_node.eval()
        assert result == 42.0

    def test_print_with_string(self, scene: Scene):
        """Test print node with string value."""
        print_node = PrintNode(scene)
        constant_node = ConstantNode(scene)

        constant_node.content.edit.setText("hello")
        constant_node.eval()

        print_node.getInput = lambda idx: constant_node if idx == 0 else None

        result = print_node.eval()
        assert result == "hello"

    def test_print_no_input_marks_invalid(self, scene: Scene):
        """Test print node marks invalid with no input."""
        node = PrintNode(scene)

        result = node.eval()
        assert result is None
        assert node.isInvalid() is True


class TestCommentNode:
    """Test suite for CommentNode."""

    def test_create_comment_node(self, scene: Scene):
        """Test creating a comment node."""
        node = CommentNode(scene)
        assert node is not None
        assert node.op_code == 82
        assert node.op_title == "Comment"
        assert len(node.inputs) == 0
        assert len(node.outputs) == 0

    def test_comment_eval_returns_none(self, scene: Scene):
        """Test comment node eval returns None."""
        node = CommentNode(scene)

        result = node.eval()
        assert result is None

    def test_comment_serialization(self, scene: Scene):
        """Test comment node serialization."""
        node = CommentNode(scene)
        node.content.edit.setPlainText("This is a test comment")

        data = node.serialize()
        assert "comment" in data
        assert data["comment"] == "This is a test comment"

    def test_comment_deserialization(self, scene: Scene):
        """Test comment node deserialization."""
        # Create and serialize a node
        node1 = CommentNode(scene)
        node1.content.edit.setPlainText("Another comment")
        data = node1.serialize()

        # Create a new node and deserialize
        node2 = CommentNode(scene)
        node2.deserialize(data, {}, True)
        assert node2.content.edit.toPlainText() == "Another comment"


class TestClampNode:
    """Test suite for ClampNode."""

    def test_create_clamp_node(self, scene: Scene):
        """Test creating a clamp node."""
        node = ClampNode(scene)
        assert node is not None
        assert node.op_code == 83
        assert node.op_title == "Clamp"
        assert len(node.inputs) == 3
        assert len(node.outputs) == 1

    def test_clamp_within_range(self, scene: Scene):
        """Test clamp with value within range."""
        clamp_node = ClampNode(scene)
        value_node = NumberInputNode(scene)
        min_node = NumberInputNode(scene)
        max_node = NumberInputNode(scene)

        value_node.content.edit.setText("5")
        min_node.content.edit.setText("0")
        max_node.content.edit.setText("10")
        value_node.eval()
        min_node.eval()
        max_node.eval()

        clamp_node.getInput = lambda idx: (
            value_node if idx == 0 else (min_node if idx == 1 else (max_node if idx == 2 else None))
        )

        result = clamp_node.eval()
        assert result == 5.0

    def test_clamp_below_minimum(self, scene: Scene):
        """Test clamp with value below minimum."""
        clamp_node = ClampNode(scene)
        value_node = NumberInputNode(scene)
        min_node = NumberInputNode(scene)
        max_node = NumberInputNode(scene)

        value_node.content.edit.setText("-5")
        min_node.content.edit.setText("0")
        max_node.content.edit.setText("10")
        value_node.eval()
        min_node.eval()
        max_node.eval()

        clamp_node.getInput = lambda idx: (
            value_node if idx == 0 else (min_node if idx == 1 else (max_node if idx == 2 else None))
        )

        result = clamp_node.eval()
        assert result == 0.0

    def test_clamp_above_maximum(self, scene: Scene):
        """Test clamp with value above maximum."""
        clamp_node = ClampNode(scene)
        value_node = NumberInputNode(scene)
        min_node = NumberInputNode(scene)
        max_node = NumberInputNode(scene)

        value_node.content.edit.setText("15")
        min_node.content.edit.setText("0")
        max_node.content.edit.setText("10")
        value_node.eval()
        min_node.eval()
        max_node.eval()

        clamp_node.getInput = lambda idx: (
            value_node if idx == 0 else (min_node if idx == 1 else (max_node if idx == 2 else None))
        )

        result = clamp_node.eval()
        assert result == 10.0

    def test_clamp_swapped_min_max(self, scene: Scene):
        """Test clamp handles swapped min/max gracefully."""
        clamp_node = ClampNode(scene)
        value_node = NumberInputNode(scene)
        min_node = NumberInputNode(scene)
        max_node = NumberInputNode(scene)

        value_node.content.edit.setText("5")
        min_node.content.edit.setText("10")  # Swapped
        max_node.content.edit.setText("0")  # Swapped
        value_node.eval()
        min_node.eval()
        max_node.eval()

        clamp_node.getInput = lambda idx: (
            value_node if idx == 0 else (min_node if idx == 1 else (max_node if idx == 2 else None))
        )

        result = clamp_node.eval()
        assert result == 5.0  # Should still clamp correctly

    def test_clamp_no_inputs_marks_invalid(self, scene: Scene):
        """Test clamp marks invalid with missing inputs."""
        node = ClampNode(scene)

        result = node.eval()
        assert result is None
        assert node.isInvalid() is True


class TestRandomNode:
    """Test suite for RandomNode."""

    def test_create_random_node(self, scene: Scene):
        """Test creating a random node."""
        node = RandomNode(scene)
        assert node is not None
        assert node.op_code == 84
        assert node.op_title == "Random"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_random_within_range(self, scene: Scene):
        """Test random generates value within range."""
        random_node = RandomNode(scene)
        min_node = NumberInputNode(scene)
        max_node = NumberInputNode(scene)

        min_node.content.edit.setText("0")
        max_node.content.edit.setText("10")
        min_node.eval()
        max_node.eval()

        random_node.getInput = lambda idx: min_node if idx == 0 else (max_node if idx == 1 else None)

        result = random_node.eval()
        assert result is not None
        assert 0.0 <= result <= 10.0

    def test_random_multiple_calls_different_values(self, scene: Scene):
        """Test random generates different values on multiple calls."""
        random_node = RandomNode(scene)
        min_node = NumberInputNode(scene)
        max_node = NumberInputNode(scene)

        min_node.content.edit.setText("0")
        max_node.content.edit.setText("100")
        min_node.eval()
        max_node.eval()

        random_node.getInput = lambda idx: min_node if idx == 0 else (max_node if idx == 1 else None)

        results = [random_node.eval() for _ in range(10)]
        # Very unlikely all 10 values are the same
        assert len(set(results)) > 1

    def test_random_swapped_min_max(self, scene: Scene):
        """Test random handles swapped min/max gracefully."""
        random_node = RandomNode(scene)
        min_node = NumberInputNode(scene)
        max_node = NumberInputNode(scene)

        min_node.content.edit.setText("10")  # Swapped
        max_node.content.edit.setText("0")  # Swapped
        min_node.eval()
        max_node.eval()

        random_node.getInput = lambda idx: min_node if idx == 0 else (max_node if idx == 1 else None)

        result = random_node.eval()
        assert result is not None
        assert 0.0 <= result <= 10.0

    def test_random_no_inputs_marks_invalid(self, scene: Scene):
        """Test random marks invalid with missing inputs."""
        node = RandomNode(scene)

        result = node.eval()
        assert result is None
        assert node.isInvalid() is True
