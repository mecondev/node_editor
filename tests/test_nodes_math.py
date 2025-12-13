"""Tests for math operation nodes.

Basic operations: Add, Subtract, Multiply, Divide
Extended operations: Power, Sqrt, Abs, Min, Max, Round, Modulo

Author:
    Michael Economou

Date:
    2025-12-12
"""

import pytest

from node_editor.core.scene import Scene
from node_editor.nodes.input_node import NumberInputNode
from node_editor.nodes.math_nodes import (
    AbsNode,
    AddNode,
    DivideNode,
    MaxNode,
    MinNode,
    ModuloNode,
    MultiplyNode,
    PowerNode,
    RoundNode,
    SqrtNode,
    SubtractNode,
)


class TestAddNode:
    """Test suite for AddNode."""

    def test_create_add_node(self, scene: Scene):
        """Test creating an add node."""
        node = AddNode(scene)
        assert node is not None
        assert node.op_code == 10
        assert node.op_title == "Add"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_add_positive_numbers(self, scene: Scene):
        """Test adding two positive numbers."""
        node = AddNode(scene)
        result = node.evalOperation(5, 3)
        assert result == 8

    def test_add_negative_numbers(self, scene: Scene):
        """Test adding two negative numbers."""
        node = AddNode(scene)
        result = node.evalOperation(-5, -3)
        assert result == -8

    def test_add_mixed_signs(self, scene: Scene):
        """Test adding positive and negative numbers."""
        node = AddNode(scene)
        result = node.evalOperation(10, -3)
        assert result == 7

    def test_add_zero(self, scene: Scene):
        """Test adding zero."""
        node = AddNode(scene)
        result = node.evalOperation(42, 0)
        assert result == 42

    def test_add_floats(self, scene: Scene):
        """Test adding floating point numbers."""
        node = AddNode(scene)
        result = node.evalOperation(1.5, 2.3)
        assert result == pytest.approx(3.8)


class TestSubtractNode:
    """Test suite for SubtractNode."""

    def test_create_subtract_node(self, scene: Scene):
        """Test creating a subtract node."""
        node = SubtractNode(scene)
        assert node is not None
        assert node.op_code == 11
        assert node.op_title == "Subtract"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_subtract_positive_numbers(self, scene: Scene):
        """Test subtracting positive numbers."""
        node = SubtractNode(scene)
        result = node.evalOperation(10, 3)
        assert result == 7

    def test_subtract_negative_result(self, scene: Scene):
        """Test subtraction resulting in negative."""
        node = SubtractNode(scene)
        result = node.evalOperation(3, 10)
        assert result == -7

    def test_subtract_negative_numbers(self, scene: Scene):
        """Test subtracting negative numbers."""
        node = SubtractNode(scene)
        result = node.evalOperation(-5, -3)
        assert result == -2

    def test_subtract_zero(self, scene: Scene):
        """Test subtracting zero."""
        node = SubtractNode(scene)
        result = node.evalOperation(42, 0)
        assert result == 42

    def test_subtract_from_zero(self, scene: Scene):
        """Test subtracting from zero."""
        node = SubtractNode(scene)
        result = node.evalOperation(0, 5)
        assert result == -5

    def test_subtract_floats(self, scene: Scene):
        """Test subtracting floating point numbers."""
        node = SubtractNode(scene)
        result = node.evalOperation(5.5, 2.3)
        assert result == pytest.approx(3.2)


class TestMultiplyNode:
    """Test suite for MultiplyNode."""

    def test_create_multiply_node(self, scene: Scene):
        """Test creating a multiply node."""
        node = MultiplyNode(scene)
        assert node is not None
        assert node.op_code == 12
        assert node.op_title == "Multiply"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_multiply_positive_numbers(self, scene: Scene):
        """Test multiplying positive numbers."""
        node = MultiplyNode(scene)
        result = node.evalOperation(6, 7)
        assert result == 42

    def test_multiply_by_zero(self, scene: Scene):
        """Test multiplying by zero."""
        node = MultiplyNode(scene)
        result = node.evalOperation(42, 0)
        assert result == 0

    def test_multiply_negative_numbers(self, scene: Scene):
        """Test multiplying two negative numbers."""
        node = MultiplyNode(scene)
        result = node.evalOperation(-4, -5)
        assert result == 20

    def test_multiply_mixed_signs(self, scene: Scene):
        """Test multiplying positive and negative."""
        node = MultiplyNode(scene)
        result = node.evalOperation(5, -3)
        assert result == -15

    def test_multiply_by_one(self, scene: Scene):
        """Test multiplying by one."""
        node = MultiplyNode(scene)
        result = node.evalOperation(42, 1)
        assert result == 42

    def test_multiply_floats(self, scene: Scene):
        """Test multiplying floating point numbers."""
        node = MultiplyNode(scene)
        result = node.evalOperation(2.5, 4.0)
        assert result == pytest.approx(10.0)


class TestDivideNode:
    """Test suite for DivideNode."""

    def test_create_divide_node(self, scene: Scene):
        """Test creating a divide node."""
        node = DivideNode(scene)
        assert node is not None
        assert node.op_code == 13
        assert node.op_title == "Divide"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_divide_positive_numbers(self, scene: Scene):
        """Test dividing positive numbers."""
        node = DivideNode(scene)
        result = node.evalOperation(10, 2)
        assert result == 5.0

    def test_divide_with_remainder(self, scene: Scene):
        """Test division with remainder."""
        node = DivideNode(scene)
        result = node.evalOperation(7, 2)
        assert result == pytest.approx(3.5)

    def test_divide_negative_numbers(self, scene: Scene):
        """Test dividing two negative numbers."""
        node = DivideNode(scene)
        result = node.evalOperation(-10, -2)
        assert result == 5.0

    def test_divide_mixed_signs(self, scene: Scene):
        """Test dividing positive by negative."""
        node = DivideNode(scene)
        result = node.evalOperation(10, -2)
        assert result == -5.0

    def test_divide_by_one(self, scene: Scene):
        """Test dividing by one."""
        node = DivideNode(scene)
        result = node.evalOperation(42, 1)
        assert result == 42.0

    def test_divide_zero_by_number(self, scene: Scene):
        """Test dividing zero by a number."""
        node = DivideNode(scene)
        result = node.evalOperation(0, 5)
        assert result == 0.0

    def test_divide_by_zero_raises_error(self, scene: Scene):
        """Test division by zero raises ZeroDivisionError."""
        node = DivideNode(scene)
        with pytest.raises(ZeroDivisionError):
            node.evalOperation(10, 0)

    def test_divide_floats(self, scene: Scene):
        """Test dividing floating point numbers."""
        node = DivideNode(scene)
        result = node.evalOperation(7.5, 2.5)
        assert result == pytest.approx(3.0)


class TestMathNodeIntegration:
    """Integration tests for math nodes with actual connections."""

    def test_math_no_inputs_connected(self, scene: Scene):
        """Test math node with no inputs returns None and marks invalid."""
        node = AddNode(scene)
        result = node.eval()
        assert result is None
        assert node.is_invalid() is True

    def test_math_one_input_missing(self, scene: Scene):
        """Test math node with only one input connected."""
        node = AddNode(scene)
        input1 = NumberInputNode(scene)
        input1.content.edit.setText("5")
        input1.eval()

        # Mock one connection
        node.get_input = lambda idx: input1 if idx == 0 else None

        result = node.eval()
        assert result is None
        assert node.is_invalid() is True

    def test_add_with_connected_inputs(self, scene: Scene):
        """Test add node with two connected inputs."""
        add_node = AddNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("10")
        input2.content.edit.setText("5")
        input1.eval()
        input2.eval()

        # Mock connections
        add_node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = add_node.eval()
        assert result == 15.0
        assert add_node.is_invalid() is False

    def test_divide_by_zero_marks_invalid(self, scene: Scene):
        """Test divide node handles division by zero gracefully."""
        div_node = DivideNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("10")
        input2.content.edit.setText("0")
        input1.eval()
        input2.eval()

        # Mock connections
        div_node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = div_node.eval()
        assert result is None
        assert div_node.is_invalid() is True

    def test_chain_math_operations(self, scene: Scene):
        """Test chaining multiple math operations."""
        # Create nodes: (10 + 5) * 2 = 30
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)
        input3 = NumberInputNode(scene)
        add_node = AddNode(scene)
        mul_node = MultiplyNode(scene)

        input1.content.edit.setText("10")
        input2.content.edit.setText("5")
        input3.content.edit.setText("2")
        input1.eval()
        input2.eval()
        input3.eval()

        # Mock connections for add_node
        add_node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)
        add_result = add_node.eval()
        assert add_result == 15.0

        # Mock connections for mul_node
        mul_node.get_input = lambda idx: add_node if idx == 0 else (input3 if idx == 1 else None)
        mul_result = mul_node.eval()
        assert mul_result == 30.0


# =============================================================================
# Extended Math Operation Tests
# =============================================================================


class TestPowerNode:
    """Test suite for PowerNode."""

    def test_create_power_node(self, scene: Scene):
        """Test creating a power node."""
        node = PowerNode(scene)
        assert node is not None
        assert node.op_code == 50
        assert node.op_title == "Power"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_power_positive_exponent(self, scene: Scene):
        """Test power with positive exponent."""
        node = PowerNode(scene)
        base = NumberInputNode(scene)
        exponent = NumberInputNode(scene)

        base.content.edit.setText("2")
        exponent.content.edit.setText("3")
        base.eval()
        exponent.eval()

        node.get_input = lambda idx: base if idx == 0 else (exponent if idx == 1 else None)

        result = node.eval()
        assert result == 8.0

    def test_power_zero_exponent(self, scene: Scene):
        """Test power with zero exponent."""
        node = PowerNode(scene)
        base = NumberInputNode(scene)
        exponent = NumberInputNode(scene)

        base.content.edit.setText("5")
        exponent.content.edit.setText("0")
        base.eval()
        exponent.eval()

        node.get_input = lambda idx: base if idx == 0 else (exponent if idx == 1 else None)

        result = node.eval()
        assert result == 1.0

    def test_power_negative_exponent(self, scene: Scene):
        """Test power with negative exponent."""
        node = PowerNode(scene)
        base = NumberInputNode(scene)
        exponent = NumberInputNode(scene)

        base.content.edit.setText("2")
        exponent.content.edit.setText("-2")
        base.eval()
        exponent.eval()

        node.get_input = lambda idx: base if idx == 0 else (exponent if idx == 1 else None)

        result = node.eval()
        assert result == pytest.approx(0.25)

    def test_power_fractional_exponent(self, scene: Scene):
        """Test power with fractional exponent (root)."""
        node = PowerNode(scene)
        base = NumberInputNode(scene)
        exponent = NumberInputNode(scene)

        base.content.edit.setText("16")
        exponent.content.edit.setText("0.5")
        base.eval()
        exponent.eval()

        node.get_input = lambda idx: base if idx == 0 else (exponent if idx == 1 else None)

        result = node.eval()
        assert result == pytest.approx(4.0)


class TestSqrtNode:
    """Test suite for SqrtNode."""

    def test_create_sqrt_node(self, scene: Scene):
        """Test creating a square root node."""
        node = SqrtNode(scene)
        assert node is not None
        assert node.op_code == 51
        assert node.op_title == "Square Root"
        assert len(node.inputs) == 1
        assert len(node.outputs) == 1

    def test_sqrt_perfect_square(self, scene: Scene):
        """Test square root of perfect square."""
        node = SqrtNode(scene)
        input_node = NumberInputNode(scene)

        input_node.content.edit.setText("16")
        input_node.eval()

        node.get_input = lambda idx: input_node if idx == 0 else None

        result = node.eval()
        assert result == 4.0

    def test_sqrt_non_perfect_square(self, scene: Scene):
        """Test square root of non-perfect square."""
        node = SqrtNode(scene)
        input_node = NumberInputNode(scene)

        input_node.content.edit.setText("2")
        input_node.eval()

        node.get_input = lambda idx: input_node if idx == 0 else None

        result = node.eval()
        assert result == pytest.approx(1.414213562)

    def test_sqrt_zero(self, scene: Scene):
        """Test square root of zero."""
        node = SqrtNode(scene)
        input_node = NumberInputNode(scene)

        input_node.content.edit.setText("0")
        input_node.eval()

        node.get_input = lambda idx: input_node if idx == 0 else None

        result = node.eval()
        assert result == 0.0

    def test_sqrt_negative_marks_invalid(self, scene: Scene):
        """Test square root of negative number marks invalid."""
        node = SqrtNode(scene)
        input_node = NumberInputNode(scene)

        input_node.content.edit.setText("-4")
        input_node.eval()

        node.get_input = lambda idx: input_node if idx == 0 else None

        result = node.eval()
        assert result is None
        assert node.is_invalid() is True


class TestAbsNode:
    """Test suite for AbsNode."""

    def test_create_abs_node(self, scene: Scene):
        """Test creating an absolute value node."""
        node = AbsNode(scene)
        assert node is not None
        assert node.op_code == 52
        assert node.op_title == "Absolute"
        assert len(node.inputs) == 1
        assert len(node.outputs) == 1

    def test_abs_positive_number(self, scene: Scene):
        """Test absolute value of positive number."""
        node = AbsNode(scene)
        input_node = NumberInputNode(scene)

        input_node.content.edit.setText("42")
        input_node.eval()

        node.get_input = lambda idx: input_node if idx == 0 else None

        result = node.eval()
        assert result == 42.0

    def test_abs_negative_number(self, scene: Scene):
        """Test absolute value of negative number."""
        node = AbsNode(scene)
        input_node = NumberInputNode(scene)

        input_node.content.edit.setText("-42")
        input_node.eval()

        node.get_input = lambda idx: input_node if idx == 0 else None

        result = node.eval()
        assert result == 42.0

    def test_abs_zero(self, scene: Scene):
        """Test absolute value of zero."""
        node = AbsNode(scene)
        input_node = NumberInputNode(scene)

        input_node.content.edit.setText("0")
        input_node.eval()

        node.get_input = lambda idx: input_node if idx == 0 else None

        result = node.eval()
        assert result == 0.0


class TestMinNode:
    """Test suite for MinNode."""

    def test_create_min_node(self, scene: Scene):
        """Test creating a minimum node."""
        node = MinNode(scene)
        assert node is not None
        assert node.op_code == 53
        assert node.op_title == "Minimum"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_min_first_smaller(self, scene: Scene):
        """Test minimum when first input is smaller."""
        node = MinNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("5")
        input2.content.edit.setText("10")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result == 5.0

    def test_min_second_smaller(self, scene: Scene):
        """Test minimum when second input is smaller."""
        node = MinNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("10")
        input2.content.edit.setText("5")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result == 5.0

    def test_min_equal_values(self, scene: Scene):
        """Test minimum with equal values."""
        node = MinNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("7")
        input2.content.edit.setText("7")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result == 7.0

    def test_min_negative_numbers(self, scene: Scene):
        """Test minimum with negative numbers."""
        node = MinNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("-5")
        input2.content.edit.setText("-10")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result == -10.0


class TestMaxNode:
    """Test suite for MaxNode."""

    def test_create_max_node(self, scene: Scene):
        """Test creating a maximum node."""
        node = MaxNode(scene)
        assert node is not None
        assert node.op_code == 54
        assert node.op_title == "Maximum"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_max_first_larger(self, scene: Scene):
        """Test maximum when first input is larger."""
        node = MaxNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("10")
        input2.content.edit.setText("5")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result == 10.0

    def test_max_second_larger(self, scene: Scene):
        """Test maximum when second input is larger."""
        node = MaxNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("5")
        input2.content.edit.setText("10")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result == 10.0

    def test_max_negative_numbers(self, scene: Scene):
        """Test maximum with negative numbers."""
        node = MaxNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("-5")
        input2.content.edit.setText("-10")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result == -5.0


class TestRoundNode:
    """Test suite for RoundNode."""

    def test_create_round_node(self, scene: Scene):
        """Test creating a round node."""
        node = RoundNode(scene)
        assert node is not None
        assert node.op_code == 55
        assert node.op_title == "Round"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_round_to_zero_places(self, scene: Scene):
        """Test rounding to zero decimal places."""
        node = RoundNode(scene)
        number = NumberInputNode(scene)
        places = NumberInputNode(scene)

        number.content.edit.setText("3.7")
        places.content.edit.setText("0")
        number.eval()
        places.eval()

        node.get_input = lambda idx: number if idx == 0 else (places if idx == 1 else None)

        result = node.eval()
        assert result == 4.0

    def test_round_to_two_places(self, scene: Scene):
        """Test rounding to two decimal places."""
        node = RoundNode(scene)
        number = NumberInputNode(scene)
        places = NumberInputNode(scene)

        number.content.edit.setText("3.14159")
        places.content.edit.setText("2")
        number.eval()
        places.eval()

        node.get_input = lambda idx: number if idx == 0 else (places if idx == 1 else None)

        result = node.eval()
        assert result == 3.14

    def test_round_negative_number(self, scene: Scene):
        """Test rounding negative number."""
        node = RoundNode(scene)
        number = NumberInputNode(scene)
        places = NumberInputNode(scene)

        number.content.edit.setText("-3.6")
        places.content.edit.setText("0")
        number.eval()
        places.eval()

        node.get_input = lambda idx: number if idx == 0 else (places if idx == 1 else None)

        result = node.eval()
        assert result == -4.0


class TestModuloNode:
    """Test suite for ModuloNode."""

    def test_create_modulo_node(self, scene: Scene):
        """Test creating a modulo node."""
        node = ModuloNode(scene)
        assert node is not None
        assert node.op_code == 56
        assert node.op_title == "Modulo"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_modulo_even_division(self, scene: Scene):
        """Test modulo with even division."""
        node = ModuloNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("10")
        input2.content.edit.setText("5")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result == 0.0

    def test_modulo_with_remainder(self, scene: Scene):
        """Test modulo with remainder."""
        node = ModuloNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("10")
        input2.content.edit.setText("3")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result == 1.0

    def test_modulo_by_zero_marks_invalid(self, scene: Scene):
        """Test modulo by zero marks invalid."""
        node = ModuloNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("10")
        input2.content.edit.setText("0")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result is None
        assert node.is_invalid() is True

    def test_modulo_negative_numbers(self, scene: Scene):
        """Test modulo with negative numbers."""
        node = ModuloNode(scene)
        input1 = NumberInputNode(scene)
        input2 = NumberInputNode(scene)

        input1.content.edit.setText("-10")
        input2.content.edit.setText("3")
        input1.eval()
        input2.eval()

        node.get_input = lambda idx: input1 if idx == 0 else (input2 if idx == 1 else None)

        result = node.eval()
        assert result == pytest.approx(2.0)  # Python modulo behavior
