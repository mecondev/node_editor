"""Base class providing serialization interface for persistent storage.

This module defines the Serializable abstract base class that all persistable
objects (nodes, edges, sockets, scenes) must inherit from. It provides a
consistent interface for converting objects to/from dictionary representations.

The serialization system uses a hashmap to track object references by ID,
enabling proper reconstruction of object graphs with circular references.

Author:
    Michael Economou

Date:
    2025-12-11
"""

from collections import OrderedDict


class Serializable:
    """Abstract base class for objects supporting dictionary serialization.

    Provides the interface for converting objects to dictionaries (for saving)
    and reconstructing them from dictionaries (for loading). Each instance
    receives a unique identifier used to maintain object references during
    serialization.

    Subclasses must implement both serialize() and deserialize() methods.

    Attributes:
        id: Unique identifier for this instance, used in serialization hashmap.
    """

    def __init__(self):
        """Initialize with a unique identifier based on object memory address."""
        self.id = id(self)

    def serialize(self) -> OrderedDict:
        """Convert this object to an ordered dictionary representation.

        Subclasses must override this to serialize their specific attributes.
        The returned dict should contain all data needed to reconstruct the
        object, including the object's id for reference tracking.

        Returns:
            Ordered dictionary containing all serializable object state.

        Raises:
            NotImplementedError: Always raised if not overridden in subclass.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement serialize()")

    def deserialize(
        self, _data: dict, _hashmap: dict | None = None, _restore_id: bool = True
    ) -> bool:
        """Reconstruct this object's state from a dictionary representation.

        Subclasses must override this to restore their specific attributes.
        The hashmap parameter allows resolving references to other serialized
        objects by their original IDs.

        Args:
            _data: Dictionary containing previously serialized object state.
            _hashmap: Maps original object IDs to reconstructed instances,
                enabling proper restoration of object references.
            _restore_id: If True, restore original ID from data. If False,
                keep current ID (useful when updating existing objects).

        Returns:
            True if deserialization completed successfully, False otherwise.

        Raises:
            NotImplementedError: Always raised if not overridden in subclass.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement deserialize()")
