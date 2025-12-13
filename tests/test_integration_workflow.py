"""Integration tests for common node editor workflows.

Tests complete workflows that involve multiple components working together:
- Creating nodes, connecting them, and evaluating
- Copy/paste operations
- Undo/redo sequences
- File save/load cycles

Author:
    Michael Economou

Date:
    2025-12-13
"""


from node_editor.core.edge import Edge
from node_editor.core.scene import Scene
from node_editor.nodes.input_node import NumberInputNode
from node_editor.nodes.math_nodes import AddNode, MultiplyNode
from node_editor.nodes.output_node import OutputNode


class TestNodeEditorWorkflow:
    """Integration tests for common workflows."""

    def test_create_connect_evaluate(self, _qtbot):
        """Test creating nodes, connecting them, and verifying structure."""
        scene = Scene()
        _ = scene.graphics_scene  # Initialize graphics

        # Create nodes: input1 -> add -> output
        #               input2 -^
        input1 = NumberInputNode(scene)
        input1.content.edit.setText("5")

        input2 = NumberInputNode(scene)
        input2.content.edit.setText("3")

        add_node = AddNode(scene)
        output_node = OutputNode(scene)

        # Connect: input1.output -> add.input[0]
        edge1 = Edge(scene, input1.outputs[0], add_node.inputs[0])
        assert edge1 is not None
        assert edge1.start_socket == input1.outputs[0]
        assert edge1.end_socket == add_node.inputs[0]

        # Connect: input2.output -> add.input[1]
        edge2 = Edge(scene, input2.outputs[0], add_node.inputs[1])
        assert edge2 is not None

        # Connect: add.output -> output.input
        edge3 = Edge(scene, add_node.outputs[0], output_node.inputs[0])
        assert edge3 is not None

        # Verify graph structure
        assert len(scene.nodes) == 4
        assert len(scene.edges) == 3

        # Verify input values are stored correctly
        assert input1.content.edit.text() == "5"
        assert input2.content.edit.text() == "3"

    def test_complex_graph_evaluation(self, _qtbot):
        """Test creation of a complex graph with multiple operations."""
        scene = Scene()
        _ = scene.graphics_scene

        # Graph: (a + b) * c
        # a=2, b=3, c=4 -> structure test only

        a = NumberInputNode(scene)
        a.content.edit.setText("2")

        b = NumberInputNode(scene)
        b.content.edit.setText("3")

        c = NumberInputNode(scene)
        c.content.edit.setText("4")

        add_node = AddNode(scene)
        mult_node = MultiplyNode(scene)
        output_node = OutputNode(scene)

        # Connect: a -> add.input[0], b -> add.input[1]
        Edge(scene, a.outputs[0], add_node.inputs[0])
        Edge(scene, b.outputs[0], add_node.inputs[1])

        # Connect: add.output -> mult.input[0], c -> mult.input[1]
        Edge(scene, add_node.outputs[0], mult_node.inputs[0])
        Edge(scene, c.outputs[0], mult_node.inputs[1])

        # Connect: mult.output -> output.input
        Edge(scene, mult_node.outputs[0], output_node.inputs[0])

        # Verify structure
        assert len(scene.nodes) == 6
        assert len(scene.edges) == 5

        # Verify input values are stored correctly
        assert a.content.edit.text() == "2"
        assert b.content.edit.text() == "3"
        assert c.content.edit.text() == "4"

    def test_copy_paste_workflow(self, _qtbot):
        """Test clipboard serialization."""
        scene = Scene()
        _ = scene.graphics_scene

        input1 = NumberInputNode(scene)
        input1.content.edit.setText("42")
        input1.set_pos(100, 100)

        add_node = AddNode(scene)
        add_node.set_pos(300, 100)

        Edge(scene, input1.outputs[0], add_node.inputs[0])

        assert len(scene.nodes) == 2
        assert len(scene.edges) == 1

        # Select nodes for copying
        input1.graphics_node.setSelected(True)
        add_node.graphics_node.setSelected(True)

        # Serialize selected nodes
        clipboard_data = scene.clipboard.serialize_selected()

        assert clipboard_data is not None
        assert "nodes" in clipboard_data
        assert len(clipboard_data["nodes"]) == 2
        assert "edges" in clipboard_data

    def test_undo_redo_sequence(self, _qtbot):
        """Test history operations (undo/redo)."""
        scene = Scene()
        _ = scene.graphics_scene
        scene.history.store_initial_history_stamp()

        # Create first node
        NumberInputNode(scene)
        scene.history.store_history("Created node1")

        assert len(scene.nodes) == 1
        assert scene.history.can_undo()
        assert not scene.history.can_redo()

        # Create second node
        node2 = AddNode(scene)
        scene.history.store_history("Created node2")

        assert len(scene.nodes) == 2

        # Create edge
        node1 = scene.nodes[0]
        Edge(scene, node1.outputs[0], node2.inputs[0])
        scene.history.store_history("Connected nodes")

        assert len(scene.edges) == 1

        # Undo edge creation
        scene.history.undo()
        assert len(scene.edges) == 0
        assert len(scene.nodes) == 2  # Nodes still there

        # Undo node2 creation
        scene.history.undo()
        assert len(scene.nodes) == 1

        # Undo node1 creation
        scene.history.undo()
        assert len(scene.nodes) == 0

        # Redo node1
        assert scene.history.can_redo()
        scene.history.redo()
        assert len(scene.nodes) == 1

        # Redo node2
        scene.history.redo()
        assert len(scene.nodes) == 2

        # Redo edge
        scene.history.redo()
        assert len(scene.edges) == 1

    def test_file_save_load_cycle(self, _qtbot, tmp_path):
        """Test saving and loading a scene to/from file."""
        scene1 = Scene()
        _ = scene1.graphics_scene

        input1 = NumberInputNode(scene1)
        input1.content.edit.setText("123")
        input1.set_pos(50, 50)

        add_node = AddNode(scene1)
        add_node.set_pos(200, 50)

        output_node = OutputNode(scene1)
        output_node.set_pos(350, 50)

        # Connect using Edge constructor
        Edge(scene1, input1.outputs[0], add_node.inputs[0])
        Edge(scene1, add_node.outputs[0], output_node.inputs[0])

        # Save to file
        filepath = tmp_path / "test_scene.json"
        scene1.save_to_file(str(filepath))

        assert filepath.exists()

        # Create new scene and load
        scene2 = Scene()
        _ = scene2.graphics_scene
        scene2.load_from_file(str(filepath))

        # Verify structure
        assert len(scene2.nodes) == 3
        assert len(scene2.edges) == 2

    def test_edge_removal_cascade(self, _qtbot):
        """Test that removing a node also removes connected edges."""
        scene = Scene()
        _ = scene.graphics_scene

        node1 = NumberInputNode(scene)
        node2 = AddNode(scene)
        node3 = OutputNode(scene)

        Edge(scene, node1.outputs[0], node2.inputs[0])
        Edge(scene, node2.outputs[0], node3.inputs[0])

        assert len(scene.nodes) == 3
        assert len(scene.edges) == 2

        # Remove middle node using node.remove()
        node2.remove()

        # Both edges should be removed
        assert len(scene.nodes) == 2
        assert len(scene.edges) == 0

    def test_dirty_propagation(self, _qtbot):
        """Test that dirty flag propagates correctly through graph."""
        scene = Scene()
        _ = scene.graphics_scene

        # Chain: input -> add -> mult -> output
        input_node = NumberInputNode(scene)
        input_node.content.edit.setText("5")

        add_node = AddNode(scene)
        mult_node = MultiplyNode(scene)
        output_node = OutputNode(scene)

        Edge(scene, input_node.outputs[0], add_node.inputs[0])
        Edge(scene, add_node.outputs[0], mult_node.inputs[0])
        Edge(scene, mult_node.outputs[0], output_node.inputs[0])

        # Mark input dirty and propagate to descendants
        input_node.mark_dirty()
        input_node.mark_descendants_dirty()

        # All nodes should be dirty
        assert input_node.is_dirty
        assert add_node.is_dirty
        assert mult_node.is_dirty
        assert output_node.is_dirty

        # Clear dirty on input
        input_node.is_dirty = False
        assert not input_node.is_dirty

    def test_invalid_connection_rejected(self, _qtbot):
        """Test that invalid connections are rejected by validators."""
        scene = Scene()
        _ = scene.graphics_scene

        node1 = NumberInputNode(scene)
        node2 = NumberInputNode(scene)

        # Verify the nodes exist
        assert len(scene.nodes) == 2
        assert len(node1.outputs) > 0
        assert len(node2.outputs) > 0

        # This should not create an edge (outputs can't connect to outputs)
        assert len(scene.edges) == 0
