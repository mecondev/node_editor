"""
Base Node Classes - Foundation for creating custom nodes.

Usage:
    from node_editor.nodes import BaseNode, NodeRegistry

    @NodeRegistry.register(100)
    class MyNode(BaseNode):
        op_title = "My Custom Node"
        category = "Custom"

        def __init__(self, scene):
            super().__init__(scene, inputs=[1], outputs=[1])

        def eval(self):
            # Get input value
            input_val = self.get_input_value(0)
            # Process
            result = input_val * 2
            # Set output
            self._value = result
            return result

Author: Michael Economou
Date: 2025-12-11
"""


class BaseNode:
    """Base class for all custom nodes.

    Subclass this to create your own node types.

    Class Attributes:
        op_code: Unique identifier (set by registry)
        op_title: Display title for the node
        category: Category for grouping in UI
        icon: Path to icon file (optional)

    Instance Attributes:
        scene: Reference to the scene
        value: Cached output value
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
        """Initialize the node.

        Args:
            scene: The scene this node belongs to
            inputs: List of input socket types
            outputs: List of output socket types
        """
        # This will be replaced with actual Node init after migration
        self.scene = scene
        self._value = None
        self._inputs = inputs or []
        self._outputs = outputs or []

    @property
    def value(self):
        """Get the cached output value."""
        return self._value

    def eval(self):
        """Evaluate this node and return the result.

        Override this method in subclasses to implement node logic.

        Returns:
            The computed value

        Raises:
            NotImplementedError: If not overridden in subclass
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement eval()")

    def get_input_value(self, index: int):
        """Get the value from an input socket.

        Args:
            index: Input socket index

        Returns:
            The value from the connected node, or None if not connected
        """
        # This will be implemented after core migration

    def on_input_changed(self, _socket=None):
        """Called when an input connection changes.

        Override to add custom behavior.

        Args:
            socket: The socket that changed (optional)
        """
        self.mark_dirty()
        self.eval()

    def mark_dirty(self, dirty: bool = True):
        """Mark this node as needing re-evaluation.

        Args:
            dirty: Whether the node is dirty
        """
        # This will be implemented after core migration

    def mark_invalid(self, invalid: bool = True):
        """Mark this node as having invalid inputs.

        Args:
            invalid: Whether the node is invalid
        """
        # This will be implemented after core migration

    def serialize(self) -> dict:
        """Serialize node to dictionary.

        Returns:
            Dictionary representation of the node
        """
        return {
            "op_code": self.__class__.op_code,
        }

    def deserialize(self, _data: dict, _hashmap: dict | None = None) -> bool:
        """Deserialize node from dictionary.

        Args:
            data: Dictionary with node data
            hashmap: Optional map for ID translation

        Returns:
            True if successful
        """
        return True


class EvaluableNode(BaseNode):
    """Node that supports automatic evaluation propagation.

    Use this as base class for nodes that need automatic
    re-evaluation when inputs change.
    """

    def __init__(self, scene, inputs=None, outputs=None):
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
