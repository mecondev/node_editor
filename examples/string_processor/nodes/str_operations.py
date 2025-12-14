"""String Processor - String Operation Nodes.

Provides nodes for string manipulation operations.

Author: Michael Economou
Date: 2025-12-14
"""

from examples.string_processor.str_conf import (
    OP_NODE_CONCAT,
    OP_NODE_FORMAT,
    OP_NODE_LENGTH,
    OP_NODE_SPLIT,
    OP_NODE_SUBSTRING,
    register_node,
)
from examples.string_processor.str_node_base import StrNode, StrOpGraphicsNode, get_icon_path


@register_node(OP_NODE_CONCAT)
class StrConcat(StrNode):
    """Node for concatenating two strings.

    Joins two string values together (a + b).

    Op Code: 203
    Inputs: 2 (string values)
    Outputs: 1 (concatenated string)
    """

    icon = get_icon_path("icons/concat.svg")
    op_code = OP_NODE_CONCAT
    op_title = "Concatenate"
    content_label = "+"
    content_label_objname = "str_node_concat"

    _graphics_node_class = StrOpGraphicsNode

    def __init__(self, scene):
        """Create a concatenate node."""
        super().__init__(scene, inputs=[5, 5], outputs=[5])

    def eval_operation(self, input1, input2):
        """Concatenate two strings.

        Args:
            input1: First string.
            input2: Second string.

        Returns:
            Concatenated string.
        """
        return str(input1) + str(input2)


@register_node(OP_NODE_FORMAT)
class StrFormat(StrNode):
    """Node for formatting strings with placeholders.

    Uses Python string format with {} placeholders.

    Op Code: 204
    Inputs: 2 (template string, value)
    Outputs: 1 (formatted string)
    """

    icon = get_icon_path("icons/format.svg")
    op_code = OP_NODE_FORMAT
    op_title = "Format"
    content_label = "{}"
    content_label_objname = "str_node_format"

    _graphics_node_class = StrOpGraphicsNode

    def __init__(self, scene):
        """Create a format node."""
        super().__init__(scene, inputs=[5, 5], outputs=[5])

    def eval_operation(self, template, value):
        """Format string with value.

        Args:
            template: Template string with {} placeholders.
            value: Value to insert.

        Returns:
            Formatted string.
        """
        return str(template).format(value)


@register_node(OP_NODE_LENGTH)
class StrLength(StrNode):
    """Node for getting string length.

    Returns the number of characters in a string.

    Op Code: 205
    Inputs: 1 (string)
    Outputs: 1 (integer length)
    """

    icon = get_icon_path("icons/length.svg")
    op_code = OP_NODE_LENGTH
    op_title = "Length"
    content_label = "#"
    content_label_objname = "str_node_length"

    _graphics_node_class = StrOpGraphicsNode

    def __init__(self, scene):
        """Create a length node."""
        super().__init__(scene, inputs=[5], outputs=[1])  # Output is number

    def eval_operation(self, text):
        """Get string length.

        Args:
            text: Input string.

        Returns:
            Length of the string.
        """
        return len(str(text))


@register_node(OP_NODE_SUBSTRING)
class StrSubstring(StrNode):
    """Node for extracting substring.

    Extracts a portion of a string using start and end indices.

    Op Code: 206
    Inputs: 3 (string, start, end)
    Outputs: 1 (substring)
    """

    icon = get_icon_path("icons/substring.svg")
    op_code = OP_NODE_SUBSTRING
    op_title = "Substring"
    content_label = "[:]"
    content_label_objname = "str_node_substring"

    _graphics_node_class = StrOpGraphicsNode

    def __init__(self, scene):
        """Create a substring node."""
        super().__init__(scene, inputs=[5, 1, 1], outputs=[5])

    def eval_operation(self, text, start, end):
        """Extract substring.

        Args:
            text: Input string.
            start: Start index (inclusive).
            end: End index (exclusive).

        Returns:
            Substring from start to end.
        """
        text = str(text)
        start_idx = int(start) if start else 0
        end_idx = int(end) if end else len(text)
        return text[start_idx:end_idx]


@register_node(OP_NODE_SPLIT)
class StrSplit(StrNode):
    """Node for splitting string into list.

    Splits a string by a delimiter into a list of parts.

    Op Code: 207
    Inputs: 2 (string, delimiter)
    Outputs: 1 (list of strings)
    """

    icon = get_icon_path("icons/split.svg")
    op_code = OP_NODE_SPLIT
    op_title = "Split"
    content_label = "||"
    content_label_objname = "str_node_split"

    _graphics_node_class = StrOpGraphicsNode

    def __init__(self, scene):
        """Create a split node."""
        super().__init__(scene, inputs=[5, 5], outputs=[5])  # Output is list

    def eval_operation(self, text, delimiter):
        """Split string by delimiter.

        Args:
            text: Input string.
            delimiter: Delimiter string.

        Returns:
            List of string parts.
        """
        return str(text).split(str(delimiter))
