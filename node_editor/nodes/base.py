"""Base classes for custom node implementation.

This module provides BaseNode and EvaluableNode as foundation classes
for creating custom node types in the node editor.

Usage:
    Create a custom node with automatic registration::

        from node_editor.nodes import BaseNode, NodeRegistry

        @NodeRegistry.register(100)
        class MyNode(BaseNode):
            op_title = "My Custom Node"
            category = "Custom"

            def __init__(self, scene):
                super().__init__(scene, inputs=[1], outputs=[1])

            def eval(self):
                input_val = self.get_input_value(0)
                result = input_val * 2
                self._value = result
                return result

Author:
    Michael Economou

Date:
    2025-12-11
"""


class BaseNode:
    """Base class for all custom node types.

    Subclass this to create nodes with custom behavior. Override
    the eval() method to implement node computation logic.

    Attributes:
        op_code: Unique identifier assigned by registry.
        op_title: Display title shown in node header.
        category: Category name for UI grouping.
        icon: Optional path to icon file.
        scene: Scene containing this node.
        value: Cached output value from evaluation.
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

        Args:
            index: Input socket index (0-based).

        Returns:
            Value from connected node, or None if not connected.
        """
        # This will be implemented after core migration

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

        Args:
            dirty: Whether node needs evaluation.
        """
        # This will be implemented after core migration

    def mark_invalid(self, invalid: bool = True):
        """Mark this node as having invalid state.

        Args:
            invalid: Whether node has invalid inputs.
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
    """Node with automatic evaluation propagation.

    Extends BaseNode with automatic dirty propagation through
    the node graph when inputs change.

    Attributes:
        Inherits all attributes from BaseNode.
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
