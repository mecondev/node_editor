"""Tests for input nodes (NumberInputNode, TextInputNode).

Author:
    Michael Economou

Date:
    2025-12-12
"""


from node_editor.core.scene import Scene
from node_editor.nodes.input_node import NumberInputNode, TextInputNode


class TestNumberInputNode:
    """Test suite for NumberInputNode."""

    def test_create_number_input_node(self, scene: Scene):
        """Test creating a number input node."""
        node = NumberInputNode(scene)
        assert node is not None
        assert node.op_code == 1
        assert node.op_title == "Number Input"
        assert len(node.inputs) == 0
        assert len(node.outputs) == 1

    def test_number_input_default_value(self, scene: Scene):
        """Test default value is 0.0."""
        node = NumberInputNode(scene)
        assert node.value == 0.0

    def test_number_input_set_value(self, scene: Scene):
        """Test setting a numeric value."""
        node = NumberInputNode(scene)
        node.content.edit.setText("42.5")
        node.eval()
        assert node.value == 42.5

    def test_number_input_integer(self, scene: Scene):
        """Test parsing integer values."""
        node = NumberInputNode(scene)
        node.content.edit.setText("100")
        node.eval()
        assert node.value == 100.0

    def test_number_input_negative(self, scene: Scene):
        """Test parsing negative values."""
        node = NumberInputNode(scene)
        node.content.edit.setText("-25.3")
        node.eval()
        assert node.value == -25.3

    def test_number_input_zero(self, scene: Scene):
        """Test zero value."""
        node = NumberInputNode(scene)
        node.content.edit.setText("0")
        node.eval()
        assert node.value == 0.0

    def test_number_input_empty_string(self, scene: Scene):
        """Test empty string defaults to 0.0."""
        node = NumberInputNode(scene)
        node.content.edit.setText("")
        node.eval()
        assert node.value == 0.0

    def test_number_input_invalid_format(self, scene: Scene):
        """Test invalid number format sets value to 0.0 and marks invalid."""
        node = NumberInputNode(scene)
        node.content.edit.setText("not a number")
        node.eval()
        assert node.value == 0.0
        assert node.is_invalid() is True

    def test_number_input_scientific_notation(self, scene: Scene):
        """Test scientific notation parsing."""
        node = NumberInputNode(scene)
        node.content.edit.setText("1.5e3")
        node.eval()
        assert node.value == 1500.0

    def test_number_input_serialization(self, scene: Scene):
        """Test serializing and deserializing number input."""
        node = NumberInputNode(scene)
        node.content.edit.setText("123.45")

        # Serialize
        data = node.content.serialize()
        assert data["value"] == "123.45"

        # Deserialize
        node.content.edit.setText("")
        node.content.deserialize(data)
        assert node.content.edit.text() == "123.45"


class TestTextInputNode:
    """Test suite for TextInputNode."""

    def test_create_text_input_node(self, scene: Scene):
        """Test creating a text input node."""
        node = TextInputNode(scene)
        assert node is not None
        assert node.op_code == 2
        assert node.op_title == "Text Input"
        assert len(node.inputs) == 0
        assert len(node.outputs) == 1

    def test_text_input_default_value(self, scene: Scene):
        """Test default value is empty string."""
        node = TextInputNode(scene)
        assert node.value == ""

    def test_text_input_set_value(self, scene: Scene):
        """Test setting a text value."""
        node = TextInputNode(scene)
        node.content.edit.setText("Hello World")
        node.eval()
        assert node.value == "Hello World"

    def test_text_input_empty(self, scene: Scene):
        """Test empty text value."""
        node = TextInputNode(scene)
        node.content.edit.setText("")
        node.eval()
        assert node.value == ""

    def test_text_input_multiline(self, scene: Scene):
        """Test text with newlines."""
        node = TextInputNode(scene)
        node.content.edit.setText("Line1\\nLine2")
        node.eval()
        assert "Line1" in node.value

    def test_text_input_special_characters(self, scene: Scene):
        """Test special characters."""
        node = TextInputNode(scene)
        special = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        node.content.edit.setText(special)
        node.eval()
        assert node.value == special

    def test_text_input_unicode(self, scene: Scene):
        """Test Unicode characters."""
        node = TextInputNode(scene)
        unicode_text = "Hello 世界 🌍"
        node.content.edit.setText(unicode_text)
        node.eval()
        assert node.value == unicode_text

    def test_text_input_numbers_as_text(self, scene: Scene):
        """Test that numbers are treated as text."""
        node = TextInputNode(scene)
        node.content.edit.setText("12345")
        node.eval()
        assert node.value == "12345"
        assert isinstance(node.value, str)

    def test_text_input_serialization(self, scene: Scene):
        """Test serializing and deserializing text input."""
        node = TextInputNode(scene)
        test_text = "Test serialization"
        node.content.edit.setText(test_text)

        # Serialize
        data = node.content.serialize()
        assert data["value"] == test_text

        # Deserialize
        node.content.edit.setText("")
        node.content.deserialize(data)
        assert node.content.edit.text() == test_text

    def test_text_input_never_invalid(self, scene: Scene):
        """Test that text input never becomes invalid."""
        node = TextInputNode(scene)
        node.content.edit.setText("any text")
        node.eval()
        assert node.is_invalid() is False
