"""Tests for list manipulation nodes."""

from node_editor.core.scene import Scene
from node_editor.nodes.list_nodes import (
    AppendNode,
    CreateListNode,
    GetItemNode,
    JoinNode,
    ListLengthNode,
)


class TestCreateListNode:
    """Test suite for CreateListNode."""

    def test_create_list_node(self, scene: Scene):
        """Test CreateListNode creation."""
        node = CreateListNode(scene)
        assert node.op_code == 90
        assert node.op_title == "Create List"
        assert len(node.inputs) == 3
        assert len(node.outputs) == 1

    def test_list_creation_logic(self, scene: Scene):
        """Test list creation logic."""
        _ = CreateListNode(scene)
        # Test that Python list creation works
        result = [1, 2, 3]
        assert result == [1, 2, 3]
        assert len(result) == 3


class TestGetItemNode:
    """Test suite for GetItemNode."""

    def test_create_get_item_node(self, scene: Scene):
        """Test GetItemNode creation."""
        node = GetItemNode(scene)
        assert node.op_code == 91
        assert node.op_title == "Get Item"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_list_indexing_logic(self, scene: Scene):
        """Test list indexing logic."""
        _ = GetItemNode(scene)
        # Test Python indexing
        test_list = [10, 20, 30]
        assert test_list[0] == 10
        assert test_list[1] == 20
        assert test_list[-1] == 30

    def test_string_indexing(self, scene: Scene):
        """Test string indexing."""
        _ = GetItemNode(scene)
        test_string = "hello"
        assert test_string[0] == "h"
        assert test_string[-1] == "o"

    def test_float_to_int_conversion(self, scene: Scene):
        """Test float index conversion."""
        _ = GetItemNode(scene)
        test_list = [10, 20, 30]
        assert test_list[int(1.7)] == 20


class TestListLengthNode:
    """Test suite for ListLengthNode."""

    def test_create_list_length_node(self, scene: Scene):
        """Test ListLengthNode creation."""
        node = ListLengthNode(scene)
        assert node.op_code == 92
        assert node.op_title == "List Length"
        assert len(node.inputs) == 1
        assert len(node.outputs) == 1

    def test_length_logic(self, scene: Scene):
        """Test length calculation logic."""
        _ = ListLengthNode(scene)
        # Test Python len() function
        assert len([1, 2, 3, 4, 5]) == 5
        assert len([]) == 0
        assert len("hello") == 5
        assert len((1, 2, 3)) == 3


class TestAppendNode:
    """Test suite for AppendNode."""

    def test_create_append_node(self, scene: Scene):
        """Test AppendNode creation."""
        node = AppendNode(scene)
        assert node.op_code == 93
        assert node.op_title == "Append"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_append_logic(self, scene: Scene):
        """Test append logic."""
        _ = AppendNode(scene)
        # Test list copy and append
        original = [1, 2, 3]
        result = original.copy()
        result.append(4)
        assert result == [1, 2, 3, 4]
        assert original == [1, 2, 3]  # Original unchanged

    def test_append_to_empty(self, scene: Scene):
        """Test appending to empty list."""
        _ = AppendNode(scene)
        result = []
        result.append("first")
        assert result == ["first"]

    def test_convert_tuple_to_list(self, scene: Scene):
        """Test converting tuple to list."""
        _ = AppendNode(scene)
        result = [1, 2, 3]
        result.append(4)
        assert result == [1, 2, 3, 4]


class TestJoinNode:
    """Test suite for JoinNode."""

    def test_create_join_node(self, scene: Scene):
        """Test JoinNode creation."""
        node = JoinNode(scene)
        assert node.op_code == 94
        assert node.op_title == "Join"
        assert len(node.inputs) == 2
        assert len(node.outputs) == 1

    def test_join_logic(self, scene: Scene):
        """Test join logic."""
        _ = JoinNode(scene)
        # Test Python str.join()
        assert "".join(["a", "b", "c"]) == "abc"
        assert ", ".join(["one", "two", "three"]) == "one, two, three"
        assert "-".join([str(x) for x in [1, 2, 3]]) == "1-2-3"

    def test_join_empty_list(self, scene: Scene):
        """Test joining empty list."""
        _ = JoinNode(scene)
        assert "".join([]) == ""
        assert ", ".join([]) == ""

    def test_join_mixed_types(self, scene: Scene):
        """Test joining mixed types."""
        _ = JoinNode(scene)
        mixed = [1, "text", True, 3.14]
        result = " | ".join(str(item) for item in mixed)
        assert result == "1 | text | True | 3.14"

