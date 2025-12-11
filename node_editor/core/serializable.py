"""
Serializable base class for saving/loading objects.

Author: Michael Economou
Date: 2025-12-11
"""

from collections import OrderedDict


class Serializable:
    """Base class for objects that can be serialized to/from dictionaries.

    All objects that need to be saved to files should inherit from this class.
    Automatically assigns a unique ID to each instance.
    """

    def __init__(self):
        """Initialize serializable object with unique ID."""
        self.id = id(self)

    def serialize(self) -> OrderedDict:
        """Serialize object to OrderedDict.

        Override this method in subclasses to add object-specific data.

        Returns:
            OrderedDict containing serialized data

        Raises:
            NotImplementedError: If not implemented in subclass
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement serialize()")

    def deserialize(
        self, _data: dict, _hashmap: dict | None = None, _restore_id: bool = True
    ) -> bool:
        """Deserialize object from dictionary.

        Override this method in subclasses to restore object-specific data.

        Args:
            data: Dictionary containing serialized data
            hashmap: Helper dict with references to existing objects by ID
            restore_id: If True, restore the object's ID from data.
                       If False, keep the current ID (useful for existing objects)

        Returns:
            True if deserialization was successful, False otherwise

        Raises:
            NotImplementedError: If not implemented in subclass
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement deserialize()")
