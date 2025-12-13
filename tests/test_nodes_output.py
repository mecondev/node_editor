"""Tests for output node (OutputNode).

Author:
    Michael Economou

Date:
    2025-12-12
"""


from node_editor.core.scene import Scene
from node_editor.nodes.input_node import NumberInputNode, TextInputNode
from node_editor.nodes.output_node import OutputNode


class TestOutputNode:
    """Test suite for OutputNode."""

    def test_create_output_node(self, scene: Scene):
        """Test creating an output node."""
        node = OutputNode(scene)
        assert node is not None
        assert node.op_code == 3
        assert node.op_title == "Output"
        assert len(node.inputs) == 1
        assert len(node.outputs) == 0

    def test_output_default_value(self, scene: Scene):
        """Test default value is None."""
        node = OutputNode(scene)
        assert node.value is None

    def test_output_no_connection(self, scene: Scene):
        """Test output with no input connection."""
        node = OutputNode(scene)
        result = node.eval()
        assert result is None
        assert node.is_invalid() is True
        assert node.content.label.text() == "---"

    def test_output_number_input(self, scene: Scene):
        """Test output displaying a number."""
        # Create input node
        input_node = NumberInputNode(scene)
        input_node.content.edit.setText("42.5")
        input_node.eval()

        # Create output node
        output_node = OutputNode(scene)

        # Mock connection (simplified)
        output_node.get_input = lambda idx: input_node if idx == 0 else None

        # Evaluate
        result = output_node.eval()
        assert result == 42.5
        assert output_node.value == 42.5
        assert output_node.is_invalid() is False

    def test_output_text_input(self, scene: Scene):
        """Test output displaying text."""
        # Create input node
        input_node = TextInputNode(scene)
        input_node.content.edit.setText("Hello World")
        input_node.eval()

        # Create output node
        output_node = OutputNode(scene)

        # Mock connection
        output_node.get_input = lambda idx: input_node if idx == 0 else None

        # Evaluate
        result = output_node.eval()
        assert result == "Hello World"
        assert output_node.value == "Hello World"

    def test_output_zero(self, scene: Scene):
        """Test output displaying zero."""
        # Create input node
        input_node = NumberInputNode(scene)
        input_node.content.edit.setText("0")
        input_node.eval()

        # Create output node
        output_node = OutputNode(scene)

        # Mock connection
        output_node.get_input = lambda idx: input_node if idx == 0 else None

        # Evaluate
        result = output_node.eval()
        assert result == 0.0
        assert output_node.content.label.text() == "0.0"

    def test_output_negative_number(self, scene: Scene):
        """Test output displaying negative number."""
        # Create input node
        input_node = NumberInputNode(scene)
        input_node.content.edit.setText("-123.45")
        input_node.eval()

        # Create output node
        output_node = OutputNode(scene)

        # Mock connection
        output_node.get_input = lambda idx: input_node if idx == 0 else None

        # Evaluate
        result = output_node.eval()
        assert result == -123.45

    def test_output_boolean_true(self, scene: Scene):
        """Test output displaying boolean True."""
        output_node = OutputNode(scene)

        # Mock input returning True
        class MockNode:
            def eval(self):
                return True

        output_node.get_input = lambda idx: MockNode() if idx == 0 else None

        result = output_node.eval()
        assert result is True
        assert output_node.content.label.text() == "True"

    def test_output_boolean_false(self, scene: Scene):
        """Test output displaying boolean False."""
        output_node = OutputNode(scene)

        # Mock input returning False
        class MockNode:
            def eval(self):
                return False

        output_node.get_input = lambda idx: MockNode() if idx == 0 else None

        result = output_node.eval()
        assert result is False
        assert output_node.content.label.text() == "False"

    def test_output_set_value_method(self, scene: Scene):
        """Test the set_value method of content widget."""
        node = OutputNode(scene)

        node.content.set_value(None)
        assert node.content.label.text() == "---"

        node.content.set_value(42)
        assert node.content.label.text() == "42"

        node.content.set_value("test")
        assert node.content.label.text() == "test"

        node.content.set_value(True)
        assert node.content.label.text() == "True"

    def test_output_updates_on_eval(self, scene: Scene):
        """Test that output label updates when eval is called."""
        input_node = NumberInputNode(scene)
        output_node = OutputNode(scene)

        # Mock connection
        output_node.get_input = lambda idx: input_node if idx == 0 else None

        # First value
        input_node.content.edit.setText("10")
        input_node.eval()
        output_node.eval()
        assert output_node.content.label.text() == "10.0"

        # Changed value
        input_node.content.edit.setText("20")
        input_node.eval()
        output_node.eval()
        assert output_node.content.label.text() == "20.0"
