"""Base classes for custom node implementation.

.. warning::
    **IMPORTANT**: BaseNode is a **simplified API for tutorials and prototyping**.
    For production code, use :class:`node_editor.core.Node` directly, which provides
    the complete feature set including graphics, serialization, undo/redo, etc.

This module provides BaseNode and EvaluableNode as lightweight foundation classes
for creating custom node types. These classes are designed for:

- **Quick prototyping** - Minimal boilerplate for testing node logic
- **Tutorials** - Simplified examples without graphics complexity
- **Documentation** - Clear separation of evaluation logic from UI

**For production nodes**, inherit from :class:`node_editor.core.Node` instead:

Comparison:

+--------------------+-------------------+---------------------------+
| Feature            | BaseNode          | core.Node                 |
+====================+===================+===========================+
| Evaluation logic   | Yes               | Yes                       |
+--------------------+-------------------+---------------------------+
| Input/Output       | Stub methods      | Full socket management    |
+--------------------+-------------------+---------------------------+
| Graphics           | No                | QDMGraphicsNode           |
+--------------------+-------------------+---------------------------+
| Serialization      | Minimal           | Complete save/load        |
+--------------------+-------------------+---------------------------+
| Undo/Redo          | No                | Full history support      |
+--------------------+-------------------+---------------------------+
| Socket types       | No                | Yes (multi-type)          |
+--------------------+-------------------+---------------------------+
| Content widget     | No                | Yes (QWidget)             |
+--------------------+-------------------+---------------------------+
| Built-in nodes     | 0                 | 52 (math, logic, etc.)    |
+--------------------+-------------------+---------------------------+

Usage (prototyping):
    Create a quick test node with BaseNode::

        from node_editor.nodes import BaseNode, NodeRegistry

        @NodeRegistry.register(100)
        class MyTestNode(BaseNode):
            op_title = "Test Node"
            category = "Testing"

            def __init__(self, scene):
                super().__init__(scene, inputs=[1], outputs=[1])

            def eval(self):
                # Note: get_input_value() is a stub in BaseNode
                input_val = self.get_input_value(0)
                result = input_val * 2 if input_val else 0
                self._value = result
                return result

Usage (production):
    For real applications, use core.Node::

        from node_editor.core import Node, Socket, SOCKET_TYPE_INT
        from PyQt5.QtWidgets import QLabel

        class MyProductionNode(Node):
            op_code = 100
            op_title = "Production Node"

            def __init__(self, scene):
                super().__init__(scene, "Production Node")
                self.socket_in = Socket(self, index=0, position=LEFT_BOTTOM,
                                      socket_type=SOCKET_TYPE_INT)
                self.socket_out = Socket(self, index=0, position=RIGHT_TOP,
                                       socket_type=SOCKET_TYPE_INT)

            def initInnerClasses(self):
                self.content = QLabel("My Node")
                self.grNode = QDMGraphicsNode(self)

            def evalImplementation(self):
                input_val = self.getInput(0)
                return input_val * 2 if input_val else 0

See Also:
    - :class:`node_editor.core.Node` - Full-featured node base class
    - :mod:`node_editor.nodes.math_nodes` - Examples using core.Node
    - :mod:`node_editor.nodes.registry` - Node registration system

Author:
    Michael Economou

Date:
    2025-12-11
"""


class BaseNode:
    """Lightweight base class for prototyping custom node types.

    .. warning::
        **This is a simplified API for tutorials/prototyping only.**
        For production nodes with full graphics, serialization, and UI support,
        use :class:`node_editor.core.Node` instead.

    BaseNode provides minimal scaffolding for node evaluation logic without
    the overhead of graphics or UI components. Methods like get_input_value(),
    mark_dirty(), and mark_invalid() are stubs here - they work fully only
    when using :class:`node_editor.core.Node`.

    **When to use:**

    - Quick testing of node evaluation algorithms
    - Tutorial code showing evaluation concepts
    - Prototype nodes before full implementation

    **When NOT to use:**

    - Production applications (use core.Node)
    - Nodes requiring graphics/UI (use core.Node)
    - Nodes needing serialization (use core.Node)
    - Any of the 52 built-in nodes (they use core.Node)

    Subclass this to create nodes with custom behavior. Override
    the eval() method to implement node computation logic.

    Attributes:
        op_code: Unique identifier assigned by registry.
        op_title: Display title shown in node header.
        category: Category name for UI grouping.
        icon: Optional path to icon file.
        scene: Scene containing this node.
        value: Cached output value from evaluation.

    See Also:
        :class:`node_editor.core.Node` - Full-featured production API
        :class:`EvaluableNode` - BaseNode with auto-propagation
    """

    # Override these in subclasses
    op_code: int = 0
    op_title: str = "Base Node"
    category: str = "Default"
    icon: str | None = None

    # Content label (for QSS styling)
    content_label: str = ""
    content_label_objname: str = "node_content"

    def __init__(self, scene, inputs: list | None = None, outputs: list | None = None):
        """Initialize a base node.

        Args:
            scene: Scene instance containing this node.
            inputs: List of input socket type indices.
            outputs: List of output socket type indices.
        """
        self.scene = scene
        self._value = None
        self._inputs = inputs or []
        self._outputs = outputs or []

    @property
    def value(self):
        """Get the cached output value from last evaluation."""
        return self._value

    def eval(self):
        """Evaluate this node and compute output value.

        Override this method in subclasses to implement the
        node's computation logic.

        Returns:
            Computed output value.

        Raises:
            NotImplementedError: If not overridden in subclass.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement eval()")

    def get_input_value(self, index: int):
        """Get value from a connected input socket.

        .. warning::
            This is a **stub method** in BaseNode. It will not retrieve actual
            input values. For working input retrieval, use :class:`node_editor.core.Node`
            which provides the full :meth:`getInput` implementation.

        Args:
            index: Input socket index (0-based).

        Returns:
            None (stub implementation). Use core.Node.getInput() for real functionality.

        See Also:
            :meth:`node_editor.core.Node.getInput` - Working implementation
        """
        # This will be implemented after core migration
        return None

    def on_input_changed(self, _socket=None):
        """Handle input connection changes.

        Called when an input socket is connected or disconnected.
        Default behavior marks node dirty and re-evaluates.

        Args:
            _socket: Socket that changed (optional).
        """
        self.mark_dirty()
        self.eval()

    def mark_dirty(self, dirty: bool = True):
        """Mark this node as needing re-evaluation.

        .. warning::
            This is a **stub method** in BaseNode. For working dirty state management,
            use :class:`node_editor.core.Node` which integrates with the evaluation system.

        Args:
            dirty: Whether node needs evaluation.

        See Also:
            :meth:`node_editor.core.Node.markDirty` - Working implementation
        """
        # This will be implemented after core migration

    def mark_invalid(self, invalid: bool = True):
        """Mark this node as having invalid state.

        .. warning::
            This is a **stub method** in BaseNode. For working invalid state management,
            use :class:`node_editor.core.Node` which integrates with the graphics system.

        Args:
            invalid: Whether node has invalid inputs.

        See Also:
            :meth:`node_editor.core.Node.markInvalid` - Working implementation
        """
        # This will be implemented after core migration

    def serialize(self) -> dict:
        """Serialize node state to dictionary.

        Returns:
            Dictionary containing node data.
        """
        return {
            "op_code": self.__class__.op_code,
        }

    def deserialize(self, _data: dict, _hashmap: dict | None = None) -> bool:
        """Restore node state from dictionary.

        Args:
            _data: Dictionary with serialized node data.
            _hashmap: Optional ID translation map.

        Returns:
            True if deserialization succeeded.
        """
        return True


class EvaluableNode(BaseNode):
    """Node with automatic evaluation propagation (simplified API).

    .. warning::
        **This is a simplified API for tutorials/prototyping only.**
        For production nodes, use :class:`node_editor.core.Node` which provides
        complete evaluation with dirty propagation, caching, and error handling.

    Extends BaseNode with automatic dirty propagation through the node graph
    when inputs change. The eval() method here adds basic caching and error
    handling, but lacks the full feature set of core.Node.

    **Key differences from core.Node:**

    - No graphics integration
    - No serialization support
    - Simplified error handling
    - Stub methods for dirty/invalid state

    **When to use:**

    - Prototyping evaluation algorithms
    - Testing node logic without UI
    - Learning the evaluation pattern

    **When NOT to use:**

    - Any production code (use core.Node)
    - Visual node editors (use core.Node)

    Attributes:
        Inherits all attributes from BaseNode.

    See Also:
        :class:`node_editor.core.Node` - Full production implementation
        :class:`BaseNode` - Parent class
    """

    def __init__(self, scene, inputs=None, outputs=None):
        """Initialize an evaluable node.

        Args:
            scene: Scene instance containing this node.
            inputs: List of input socket type indices.
            outputs: List of output socket types (None for no outputs)
        """
        super().__init__(scene, inputs, outputs)
        self.mark_dirty()

    def eval(self):
        """Evaluate with caching support."""
        # If already evaluated and not dirty, return cached value
        # This will be implemented after core migration
        try:
            result = self.eval_implementation()
            self._value = result
            self.mark_dirty(False)
            self.mark_invalid(False)
            return result
        except Exception:
            self.mark_invalid(True)
            raise

    def eval_implementation(self):
        """Override this to implement evaluation logic.

        Returns:
            The computed value
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement eval_implementation()")
