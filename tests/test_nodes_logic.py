"""Tests for logic operation nodes.

Comparison: Equal, NotEqual, <, <=, >, >=
Conditional: If/Switch
Boolean: AND, OR, NOT, XOR

Author:
    Michael Economou

Date:
    2025-12-12
"""


from node_editor.core.scene import Scene
from node_editor.nodes.input_node import NumberInputNode, TextInputNode
from node_editor.nodes.logic_nodes import (
    AndNode,
    EqualNode,
    GreaterEqualNode,
    GreaterThanNode,
    IfNode,
    LessEqualNode,
    LessThanNode,
    NotEqualNode,
    NotNode,
    OrNode,
    XorNode,
)


class TestEqualNode:
    """Test suite for EqualNode."""

    def test_create_equal_node(self, scene: Scene):
        """Test creating an equal node."""
        node = EqualNode(scene)
        assert node is not None
        assert node.op_code == 20
        assert node.op_title == "Equal"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_equal_same_numbers(self, scene: Scene):
        """Test equality of same numbers."""
        node = EqualNode(scene)
        assert node.compare_operation(5, 5) is True

    def test_equal_different_numbers(self, scene: Scene):
        """Test inequality of different numbers."""
        node = EqualNode(scene)
        assert node.compare_operation(5, 3) is False

    def test_equal_same_strings(self, scene: Scene):
        """Test equality of same strings."""
        node = EqualNode(scene)
        assert node.compare_operation("hello", "hello") is True

    def test_equal_different_strings(self, scene: Scene):
        """Test inequality of different strings."""
        node = EqualNode(scene)
        assert node.compare_operation("hello", "world") is False


class TestNotEqualNode:
    """Test suite for NotEqualNode."""

    def test_create_not_equal_node(self, scene: Scene):
        """Test creating a not equal node."""
        node = NotEqualNode(scene)
        assert node is not None
        assert node.op_code == 21
        assert node.op_title == "Not Equal"

    def test_not_equal_different_numbers(self, scene: Scene):
        """Test not equal with different numbers."""
        node = NotEqualNode(scene)
        assert node.compare_operation(5, 3) is True

    def test_not_equal_same_numbers(self, scene: Scene):
        """Test not equal with same numbers."""
        node = NotEqualNode(scene)
        assert node.compare_operation(5, 5) is False


class TestLessThanNode:
    """Test suite for LessThanNode."""

    def test_create_less_than_node(self, scene: Scene):
        """Test creating a less than node."""
        node = LessThanNode(scene)
        assert node is not None
        assert node.op_code == 22
        assert node.op_title == "Less Than"

    def test_less_than_true(self, scene: Scene):
        """Test less than when true."""
        node = LessThanNode(scene)
        assert node.compare_operation(3, 5) is True

    def test_less_than_false(self, scene: Scene):
        """Test less than when false."""
        node = LessThanNode(scene)
        assert node.compare_operation(5, 3) is False

    def test_less_than_equal_values(self, scene: Scene):
        """Test less than with equal values."""
        node = LessThanNode(scene)
        assert node.compare_operation(5, 5) is False


class TestLessEqualNode:
    """Test suite for LessEqualNode."""

    def test_create_less_equal_node(self, scene: Scene):
        """Test creating a less or equal node."""
        node = LessEqualNode(scene)
        assert node is not None
        assert node.op_code == 23
        assert node.op_title == "Less or Equal"

    def test_less_equal_less_than(self, scene: Scene):
        """Test less or equal when less than."""
        node = LessEqualNode(scene)
        assert node.compare_operation(3, 5) is True

    def test_less_equal_equal(self, scene: Scene):
        """Test less or equal when equal."""
        node = LessEqualNode(scene)
        assert node.compare_operation(5, 5) is True

    def test_less_equal_greater(self, scene: Scene):
        """Test less or equal when greater."""
        node = LessEqualNode(scene)
        assert node.compare_operation(7, 5) is False


class TestGreaterThanNode:
    """Test suite for GreaterThanNode."""

    def test_create_greater_than_node(self, scene: Scene):
        """Test creating a greater than node."""
        node = GreaterThanNode(scene)
        assert node is not None
        assert node.op_code == 24
        assert node.op_title == "Greater Than"

    def test_greater_than_true(self, scene: Scene):
        """Test greater than when true."""
        node = GreaterThanNode(scene)
        assert node.compare_operation(5, 3) is True

    def test_greater_than_false(self, scene: Scene):
        """Test greater than when false."""
        node = GreaterThanNode(scene)
        assert node.compare_operation(3, 5) is False

    def test_greater_than_equal_values(self, scene: Scene):
        """Test greater than with equal values."""
        node = GreaterThanNode(scene)
        assert node.compare_operation(5, 5) is False


class TestGreaterEqualNode:
    """Test suite for GreaterEqualNode."""

    def test_create_greater_equal_node(self, scene: Scene):
        """Test creating a greater or equal node."""
        node = GreaterEqualNode(scene)
        assert node is not None
        assert node.op_code == 25
        assert node.op_title == "Greater or Equal"

    def test_greater_equal_greater(self, scene: Scene):
        """Test greater or equal when greater."""
        node = GreaterEqualNode(scene)
        assert node.compare_operation(7, 5) is True

    def test_greater_equal_equal(self, scene: Scene):
        """Test greater or equal when equal."""
        node = GreaterEqualNode(scene)
        assert node.compare_operation(5, 5) is True

    def test_greater_equal_less(self, scene: Scene):
        """Test greater or equal when less."""
        node = GreaterEqualNode(scene)
        assert node.compare_operation(3, 5) is False


class TestIfNode:
    """Test suite for IfNode (conditional switch)."""

    def test_create_if_node(self, scene: Scene):
        """Test creating an if/switch node."""
        node = IfNode(scene)
        assert node is not None
        assert node.op_code == 30
        assert node.op_title == "If / Switch"
        assert len(node.inputs) == 3
        assert len(node.outputs) == 1

    def test_if_no_inputs_connected(self, scene: Scene):
        """Test if node with no inputs returns None and marks invalid."""
        node = IfNode(scene)
        result = node.eval()
        assert result is None
        assert node.is_invalid() is True

    def test_if_condition_true(self, scene: Scene):
        """Test if node returns true_value when condition is True."""
        node = IfNode(scene)

        # Mock inputs
        class MockCondition:
            def eval(self):
                return True

        class MockTrueValue:
            def eval(self):
                return 100

        class MockFalseValue:
            def eval(self):
                return 200

        node.get_input = lambda idx: (
            MockCondition() if idx == 0 else (
                MockTrueValue() if idx == 1 else (
                    MockFalseValue() if idx == 2 else None
                )
            )
        )

        result = node.eval()
        assert result == 100
        assert node.is_invalid() is False

    def test_if_condition_false(self, scene: Scene):
        """Test if node returns false_value when condition is False."""
        node = IfNode(scene)

        # Mock inputs
        class MockCondition:
            def eval(self):
                return False

        class MockTrueValue:
            def eval(self):
                return 100

        class MockFalseValue:
            def eval(self):
                return 200

        node.get_input = lambda idx: (
            MockCondition() if idx == 0 else (
                MockTrueValue() if idx == 1 else (
                    MockFalseValue() if idx == 2 else None
                )
            )
        )

        result = node.eval()
        assert result == 200
        assert node.is_invalid() is False

    def test_if_with_zero_as_false(self, scene: Scene):
        """Test if node treats 0 as False."""
        node = IfNode(scene)

        class MockCondition:
            def eval(self):
                return 0

        class MockTrueValue:
            def eval(self):
                return "true"

        class MockFalseValue:
            def eval(self):
                return "false"

        node.get_input = lambda idx: (
            MockCondition() if idx == 0 else (
                MockTrueValue() if idx == 1 else (
                    MockFalseValue() if idx == 2 else None
                )
            )
        )

        result = node.eval()
        assert result == "false"

    def test_if_with_nonzero_as_true(self, scene: Scene):
        """Test if node treats non-zero as True."""
        node = IfNode(scene)

        class MockCondition:
            def eval(self):
                return 42

        class MockTrueValue:
            def eval(self):
                return "true"

        class MockFalseValue:
            def eval(self):
                return "false"

        node.get_input = lambda idx: (
            MockCondition() if idx == 0 else (
                MockTrueValue() if idx == 1 else (
                    MockFalseValue() if idx == 2 else None
                )
            )
        )

        result = node.eval()
        assert result == "true"


class TestLogicNodeIntegration:
    """Integration tests for logic nodes with actual connections."""

    def test_compare_numbers(self, scene: Scene):
        """Test comparing two number inputs."""
        lt_node = LessThanNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("5")
        input2.content.edit.setText("10")
        input1.eval()
        input2.eval()

        # Mock connections
        lt_node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = lt_node.eval()
        assert result is True
        assert lt_node.is_invalid() is False

    def test_compare_strings(self, scene: Scene):
        """Test comparing two text inputs."""
        eq_node = EqualNode(scene)
        input1 = TextInputNode(scene)
        input2 = TextInputNode(scene)

        input1.content.edit.setText("hello")
        input2.content.edit.setText("hello")
        input1.eval()
        input2.eval()

        # Mock connections
        eq_node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = eq_node.eval()
        assert result is True

    def test_if_node_with_comparison(self, scene: Scene):
        """Test if node using comparison result as condition."""
        # Create: if (5 < 10) then "yes" else "no"
        lt_node = LessThanNode(scene)
        if_node = IfNode(scene)
        num1 = NumberInputNode(scene)
        num2 = NumberInputNode(scene)
        true_val = TextInputNode(scene)
        false_val = TextInputNode(scene)

        num1.content.edit.setText("5")
        num2.content.edit.setText("10")
        true_val.content.edit.setText("yes")
        false_val.content.edit.setText("no")

        num1.eval()
        num2.eval()
        true_val.eval()
        false_val.eval()

        # Mock connections for lt_node
        lt_node.get_input = lambda idx: num1 if idx == 0 else (num2 if idx == 1 else None)
        lt_result = lt_node.eval()
        assert lt_result is True

        # Mock connections for if_node
        if_node.get_input = lambda idx: (
            lt_node if idx == 0 else (
                true_val if idx == 1 else (
                    false_val if idx == 2 else None
                )
            )
        )

        result = if_node.eval()
        assert result == "yes"


class TestAndNode:
    """Test suite for AndNode (logical AND)."""

    def test_create_and_node(self, scene: Scene):
        """Test creating an AND node."""
        node = AndNode(scene)
        assert node is not None
        assert node.op_code == 60
        assert node.op_title == "AND"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_and_true_true(self, scene: Scene):
        """Test AND with both inputs true."""
        node = AndNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("1")
        input2.content.edit.setText("1")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is True

    def test_and_true_false(self, scene: Scene):
        """Test AND with first true, second false."""
        node = AndNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("1")
        input2.content.edit.setText("0")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is False

    def test_and_false_true(self, scene: Scene):
        """Test AND with first false, second true."""
        node = AndNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("0")
        input2.content.edit.setText("1")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is False

    def test_and_false_false(self, scene: Scene):
        """Test AND with both inputs false."""
        node = AndNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("0")
        input2.content.edit.setText("0")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is False

    def test_and_non_zero_numbers(self, scene: Scene):
        """Test AND with non-zero numbers (truthy values)."""
        node = AndNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("5")
        input2.content.edit.setText("10")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is True

    def test_and_empty_string(self, scene: Scene):
        """Test AND with empty string (falsy)."""
        node = AndNode(scene)
        input1 = TextInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("")
        input2.content.edit.setText("1")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is False


class TestOrNode:
    """Test suite for OrNode (logical OR)."""

    def test_create_or_node(self, scene: Scene):
        """Test creating an OR node."""
        node = OrNode(scene)
        assert node is not None
        assert node.op_code == 61
        assert node.op_title == "OR"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_or_true_true(self, scene: Scene):
        """Test OR with both inputs true."""
        node = OrNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("1")
        input2.content.edit.setText("1")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is True

    def test_or_true_false(self, scene: Scene):
        """Test OR with first true, second false."""
        node = OrNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("1")
        input2.content.edit.setText("0")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is True

    def test_or_false_true(self, scene: Scene):
        """Test OR with first false, second true."""
        node = OrNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("0")
        input2.content.edit.setText("1")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is True

    def test_or_false_false(self, scene: Scene):
        """Test OR with both inputs false."""
        node = OrNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("0")
        input2.content.edit.setText("0")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is False

    def test_or_non_zero_number_and_zero(self, scene: Scene):
        """Test OR with non-zero number and zero."""
        node = OrNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("5")
        input2.content.edit.setText("0")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is True


class TestNotNode:
    """Test suite for NotNode (logical NOT)."""

    def test_create_not_node(self, scene: Scene):
        """Test creating a NOT node."""
        node = NotNode(scene)
        assert node is not None
        assert node.op_code == 62
        assert node.op_title == "NOT"
        assert len(node.inputs) == 1
        assert len(node.outputs) == 1

    def test_not_true(self, scene: Scene):
        """Test NOT with true input."""
        node = NotNode(scene)
        input_node = NumberInputNode(scene)

        input_node.content.edit.setText("1")
        input_node.eval()

        node.get_input = lambda idx: input_node if idx == 0 else None

        result = node.eval()
        assert result is False

    def test_not_false(self, scene: Scene):
        """Test NOT with false input."""
        node = NotNode(scene)
        input_node = NumberInputNode(scene)

        input_node.content.edit.setText("0")
        input_node.eval()

        node.get_input = lambda idx: input_node if idx == 0 else None

        result = node.eval()
        assert result is True

    def test_not_non_zero_number(self, scene: Scene):
        """Test NOT with non-zero number (truthy)."""
        node = NotNode(scene)
        input_node = NumberInputNode(scene)

        input_node.content.edit.setText("42")
        input_node.eval()

        node.get_input = lambda idx: input_node if idx == 0 else None

        result = node.eval()
        assert result is False

    def test_not_empty_string(self, scene: Scene):
        """Test NOT with empty string (falsy)."""
        node = NotNode(scene)
        input_node = TextInputNode(scene)

        input_node.content.edit.setText("")
        input_node.eval()

        node.get_input = lambda idx: input_node if idx == 0 else None

        result = node.eval()
        assert result is True

    def test_not_non_empty_string(self, scene: Scene):
        """Test NOT with non-empty string (truthy)."""
        node = NotNode(scene)
        input_node = TextInputNode(scene)

        input_node.content.edit.setText("hello")
        input_node.eval()

        node.get_input = lambda idx: input_node if idx == 0 else None

        result = node.eval()
        assert result is False


class TestXorNode:
    """Test suite for XorNode (logical XOR)."""

    def test_create_xor_node(self, scene: Scene):
        """Test creating an XOR node."""
        node = XorNode(scene)
        assert node is not None
        assert node.op_code == 63
        assert node.op_title == "XOR"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_xor_true_true(self, scene: Scene):
        """Test XOR with both inputs true (should be false)."""
        node = XorNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("1")
        input2.content.edit.setText("1")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is False

    def test_xor_true_false(self, scene: Scene):
        """Test XOR with first true, second false (should be true)."""
        node = XorNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("1")
        input2.content.edit.setText("0")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is True

    def test_xor_false_true(self, scene: Scene):
        """Test XOR with first false, second true (should be true)."""
        node = XorNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("0")
        input2.content.edit.setText("1")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is True

    def test_xor_false_false(self, scene: Scene):
        """Test XOR with both inputs false (should be false)."""
        node = XorNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("0")
        input2.content.edit.setText("0")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is False

    def test_xor_non_zero_numbers(self, scene: Scene):
        """Test XOR with two non-zero numbers (both truthy, should be false)."""
        node = XorNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("5")
        input2.content.edit.setText("10")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is False

    def test_xor_mixed_types(self, scene: Scene):
        """Test XOR with different truthy/falsy types."""
        node = XorNode(scene)
        input1 = TextInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("hello")  # truthy
        input2.content.edit.setText("0")  # falsy
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is True
