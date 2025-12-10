"""
Node Registry - Central registry for all node types.

Usage:
    from node_editor.nodes import NodeRegistry, BaseNode
    
    # Using decorator
    @NodeRegistry.register(100)
    class MyNode(BaseNode):
        op_title = "My Node"
        ...
    
    # Manual registration
    NodeRegistry.register_node(101, AnotherNode)
    
    # Get node class
    node_class = NodeRegistry.get_node_class(100)
"""

from typing import Callable


class NodeRegistry:
    """Central registry for all node types."""

    _nodes: dict[int, type] = {}

    @classmethod
    def register(cls, op_code: int) -> Callable:
        """Decorator to register a node class.
        
        Args:
            op_code: Unique identifier for the node type.
                    Use 1-99 for built-in nodes, 100+ for custom nodes.
        
        Returns:
            Decorator function
            
        Example:
            @NodeRegistry.register(100)
            class MyNode(BaseNode):
                ...
        """
        def decorator(node_class: type) -> type:
            if op_code in cls._nodes:
                existing = cls._nodes[op_code].__name__
                raise ValueError(
                    f"OpCode {op_code} already registered to {existing}"
                )
            cls._nodes[op_code] = node_class
            node_class.op_code = op_code
            return node_class
        return decorator

    @classmethod
    def register_node(cls, op_code: int, node_class: type) -> None:
        """Manually register a node class.
        
        Args:
            op_code: Unique identifier for the node type
            node_class: The node class to register
            
        Raises:
            ValueError: If op_code is already registered
        """
        if op_code in cls._nodes:
            existing = cls._nodes[op_code].__name__
            raise ValueError(
                f"OpCode {op_code} already registered to {existing}"
            )
        cls._nodes[op_code] = node_class
        node_class.op_code = op_code

    @classmethod
    def get_node_class(cls, op_code: int) -> type | None:
        """Get node class by op_code.
        
        Args:
            op_code: The op_code to look up
            
        Returns:
            The node class or None if not found
        """
        return cls._nodes.get(op_code)

    @classmethod
    def get_all_nodes(cls) -> dict[int, type]:
        """Get all registered nodes.
        
        Returns:
            Dictionary mapping op_codes to node classes
        """
        return cls._nodes.copy()

    @classmethod
    def get_nodes_by_category(cls, category: str) -> dict[int, type]:
        """Get all nodes in a category.
        
        Args:
            category: Category name to filter by
            
        Returns:
            Dictionary of nodes in the category
        """
        return {
            op_code: node_class
            for op_code, node_class in cls._nodes.items()
            if getattr(node_class, "category", None) == category
        }

    @classmethod
    def clear(cls) -> None:
        """Clear all registered nodes (useful for testing)."""
        cls._nodes.clear()

    @classmethod
    def unregister(cls, op_code: int) -> bool:
        """Unregister a node by op_code.
        
        Args:
            op_code: The op_code to unregister
            
        Returns:
            True if node was unregistered, False if not found
        """
        if op_code in cls._nodes:
            del cls._nodes[op_code]
            return True
        return False
