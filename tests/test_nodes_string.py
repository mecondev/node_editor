"""Tests for string operation nodes.

Author:
    Michael Economou

Date:
    2025-12-12
"""


from node_editor.core.scene import Scene
from node_editor.nodes.input_node import NumberInputNode, TextInputNode
from node_editor.nodes.string_nodes import (
    ConcatenateNode,
    FormatNode,
    LengthNode,
    SplitNode,
    SubstringNode,
)


class TestConcatenateNode:
    """Test suite for ConcatenateNode."""

    def test_create_concatenate_node(self, scene: Scene):
        """Test creating a concatenate node."""
        node = ConcatenateNode(scene)
        assert node is not None
        assert node.op_code == 40
        assert node.op_title == "Concatenate"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_concatenate_two_strings(self, scene: Scene):
        """Test concatenating two strings."""
        node = ConcatenateNode(scene)
        input1 = TextInputNode(scene)
        input2 = TextInputNode(scene)

        input1.content.edit.setText("Hello")
        input2.content.edit.setText(" World")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result == "Hello World"
        assert node.is_invalid() is False

    def test_concatenate_numbers_as_strings(self, scene: Scene):
        """Test concatenating numbers (converted to strings)."""
        node = ConcatenateNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("42")
        input2.content.edit.setText("100")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result == "42.0100.0"

    def test_concatenate_empty_strings(self, scene: Scene):
        """Test concatenating empty strings."""
        node = ConcatenateNode(scene)
        input1 = TextInputNode(scene)
        input2 = TextInputNode(scene)

        input1.content.edit.setText("")
        input2.content.edit.setText("")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result == ""


class TestFormatNode:
    """Test suite for FormatNode."""

    def test_create_format_node(self, scene: Scene):
        """Test creating a format node."""
        node = FormatNode(scene)
        assert node is not None
        assert node.op_code == 41
        assert node.op_title == "Format"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_format_with_curly_braces(self, scene: Scene):
        """Test formatting with {} placeholder."""
        node = FormatNode(scene)
        template = TextInputNode(scene)
        value = NumberInputNode(scene)

        template.content.edit.setText("Value: {}")
        value.content.edit.setText("42")
        template.eval()
        value.eval()

        node.get_input = lambda idx: template if idx == 0 else (value if idx == 1 else None)

        result = node.eval()
        assert result == "Value: 42.0"

    def test_format_with_named_placeholder(self, scene: Scene):
        """Test formatting with {0} placeholder."""
        node = FormatNode(scene)
        template = TextInputNode(scene)
        value = NumberInputNode(scene)

        template.content.edit.setText("Result: {0}")
        value.content.edit.setText("100")
        template.eval()
        value.eval()

        node.get_input = lambda idx: template if idx == 0 else (value if idx == 1 else None)

        result = node.eval()
        assert result == "Result: 100.0"

    def test_format_with_text_value(self, scene: Scene):
        """Test formatting with text value."""
        node = FormatNode(scene)
        template = TextInputNode(scene)
        value = TextInputNode(scene)

        template.content.edit.setText("Hello, {}!")
        value.content.edit.setText("World")
        template.eval()
        value.eval()

        node.get_input = lambda idx: template if idx == 0 else (value if idx == 1 else None)

        result = node.eval()
        assert result == "Hello, World!"


class TestLengthNode:
    """Test suite for LengthNode."""

    def test_create_length_node(self, scene: Scene):
        """Test creating a length node."""
        node = LengthNode(scene)
        assert node is not None
        assert node.op_code == 42
        assert node.op_title == "Length"
        assert len(node.inputs) == 1
        assert len(node.outputs) == 1

    def test_length_of_string(self, scene: Scene):
        """Test getting length of a string."""
        node = LengthNode(scene)
        input_node = TextInputNode(scene)

        input_node.content.edit.setText("Hello World")
        input_node.eval()

        node.get_input = lambda idx: input_node if idx == 0 else None

        result = node.eval()
        assert result == 11

    def test_length_of_empty_string(self, scene: Scene):
        """Test getting length of empty string."""
        node = LengthNode(scene)
        input_node = TextInputNode(scene)

        input_node.content.edit.setText("")
        input_node.eval()

        node.get_input = lambda idx: input_node if idx == 0 else None

        result = node.eval()
        assert result == 0

    def test_length_of_list(self, scene: Scene):
        """Test getting length of a list."""
        node = LengthNode(scene)

        class MockListNode:
            def eval(self):
                return ["a", "b", "c", "d"]

        node.get_input = lambda idx: MockListNode() if idx == 0 else None

        result = node.eval()
        assert result == 4


class TestSubstringNode:
    """Test suite for SubstringNode."""

    def test_create_substring_node(self, scene: Scene):
        """Test creating a substring node."""
        node = SubstringNode(scene)
        assert node is not None
        assert node.op_code == 43
        assert node.op_title == "Substring"
        assert len(node.inputs) == 3
        assert len(node.outputs) == 1

    def test_substring_extraction(self, scene: Scene):
        """Test extracting a substring."""
        node = SubstringNode(scene)
        string_node = TextInputNode(scene)
        start_node = NumberInputNode(scene)
        end_node = NumberInputNode(scene)

        string_node.content.edit.setText("Hello World")
        start_node.content.edit.setText("0")
        end_node.content.edit.setText("5")
        string_node.eval()
        start_node.eval()
        end_node.eval()

        node.get_input = lambda idx: (
            string_node if idx == 0 else (
                start_node if idx == 1 else (
                    end_node if idx == 2 else None
                )
            )
        )

        result = node.eval()
        assert result == "Hello"

    def test_substring_middle(self, scene: Scene):
        """Test extracting from middle of string."""
        node = SubstringNode(scene)
        string_node = TextInputNode(scene)
        start_node = NumberInputNode(scene)
        end_node = NumberInputNode(scene)

        string_node.content.edit.setText("Hello World")
        start_node.content.edit.setText("6")
        end_node.content.edit.setText("11")
        string_node.eval()
        start_node.eval()
        end_node.eval()

        node.get_input = lambda idx: (
            string_node if idx == 0 else (
                start_node if idx == 1 else (
                    end_node if idx == 2 else None
                )
            )
        )

        result = node.eval()
        assert result == "World"

    def test_substring_negative_index(self, scene: Scene):
        """Test substring with negative indices."""
        node = SubstringNode(scene)
        string_node = TextInputNode(scene)
        start_node = NumberInputNode(scene)
        end_node = NumberInputNode(scene)

        string_node.content.edit.setText("Hello")
        start_node.content.edit.setText("-3")
        end_node.content.edit.setText("-1")
        string_node.eval()
        start_node.eval()
        end_node.eval()

        node.get_input = lambda idx: (
            string_node if idx == 0 else (
                start_node if idx == 1 else (
                    end_node if idx == 2 else None
                )
            )
        )

        result = node.eval()
        assert result == "ll"


class TestSplitNode:
    """Test suite for SplitNode."""

    def test_create_split_node(self, scene: Scene):
        """Test creating a split node."""
        node = SplitNode(scene)
        assert node is not None
        assert node.op_code == 44
        assert node.op_title == "Split"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_split_by_space(self, scene: Scene):
        """Test splitting string by space."""
        node = SplitNode(scene)
        string_node = TextInputNode(scene)
        delimiter_node = TextInputNode(scene)

        string_node.content.edit.setText("Hello World Test")
        delimiter_node.content.edit.setText(" ")
        string_node.eval()
        delimiter_node.eval()

        node.get_input = lambda idx: string_node if idx == 0 else (delimiter_node if idx == 1 else None)

        result = node.eval()
        assert result == ["Hello", "World", "Test"]

    def test_split_by_comma(self, scene: Scene):
        """Test splitting string by comma."""
        node = SplitNode(scene)
        string_node = TextInputNode(scene)
        delimiter_node = TextInputNode(scene)

        string_node.content.edit.setText("a,b,c,d")
        delimiter_node.content.edit.setText(",")
        string_node.eval()
        delimiter_node.eval()

        node.get_input = lambda idx: string_node if idx == 0 else (delimiter_node if idx == 1 else None)

        result = node.eval()
        assert result == ["a", "b", "c", "d"]

    def test_split_by_empty_delimiter(self, scene: Scene):
        """Test splitting by empty delimiter (whitespace)."""
        node = SplitNode(scene)
        string_node = TextInputNode(scene)
        delimiter_node = TextInputNode(scene)

        string_node.content.edit.setText("Hello   World")
        delimiter_node.content.edit.setText("")
        string_node.eval()
        delimiter_node.eval()

        node.get_input = lambda idx: string_node if idx == 0 else (delimiter_node if idx == 1 else None)

        result = node.eval()
        assert result == ["Hello", "World"]

    def test_split_no_delimiter_found(self, scene: Scene):
        """Test splitting when delimiter not found."""
        node = SplitNode(scene)
        string_node = TextInputNode(scene)
        delimiter_node = TextInputNode(scene)

        string_node.content.edit.setText("HelloWorld")
        delimiter_node.content.edit.setText(",")
        string_node.eval()
        delimiter_node.eval()

        node.get_input = lambda idx: string_node if idx == 0 else (delimiter_node if idx == 1 else None)

        result = node.eval()
        assert result == ["HelloWorld"]
