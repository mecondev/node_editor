"""Base classes for customizable node content widgets.

This module defines QDMNodeContentWidget, the base class for creating
custom content areas inside nodes. Subclass it to add controls,
displays, or interactive elements to your nodes.

Also provides QDMTextEdit as an example of a widget that properly
integrates with the editing state system.

Author:
    Michael Economou

Date:
    2025-12-11
"""

from collections import OrderedDict
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from node_editor.core.serializable import Serializable

if TYPE_CHECKING:
    from PyQt5.QtGui import QFocusEvent

    from node_editor.core.node import Node


class QDMNodeContentWidget(QWidget, Serializable):
    """Base class for node content area.

    Provides layout container for widgets displayed inside a node.
    Subclass and override initUI() to create custom node interfaces.

    Attributes:
        node: Parent Node containing this content.
        layout: QVBoxLayout for arranging child widgets.
    """

    def __init__(self, node: "Node", parent: QWidget | None = None):
        """Initialize content widget for a node.

        Args:
            node: Parent Node this content belongs to.
            parent: Optional parent widget.
        """
        self.node = node
        super().__init__(parent)

        self.initUI()

    def initUI(self) -> None:
        """Set up layout and child widgets.

        Override in subclasses to create custom node content.
        Default creates a label and text edit as example.
        """
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.wdg_label = QLabel("Some Title")
        self.layout.addWidget(self.wdg_label)
        self.layout.addWidget(QDMTextEdit("foo"))

    def setEditingFlag(self, value: bool) -> None:
        """Update editing state in graphics view.

        Call when starting/ending text editing to prevent view
        keyboard shortcuts from triggering while typing.

        Args:
            value: True when editing starts, False when done.
        """
        self.node.scene.getView().editingFlag = value

    def serialize(self) -> OrderedDict:
        """Serialize content widget state.

        Override to save custom widget data.

        Returns:
            OrderedDict with serialized state.
        """
        return OrderedDict([])

    def deserialize(
        self, _data: dict, _hashmap: dict | None = None, _restore_id: bool = True
    ) -> bool:
        """Restore content widget state from data.

        Override to restore custom widget data.

        Args:
            _data: Dictionary with serialized state.
            _hashmap: Map of old IDs to new objects.
            _restore_id: Whether to restore original ID.

        Returns:
            True if deserialization succeeded.
        """
        return True


class QDMTextEdit(QTextEdit):
    """Text editor with editing state integration.

    Notifies parent QDMNodeContentWidget when editing starts/stops
    so view shortcuts are properly disabled during text input.
    """

    def focusInEvent(self, event: "QFocusEvent") -> None:
        """Signal editing start when widget gains focus.

        Args:
            event: Qt focus event.
        """
        self.parentWidget().setEditingFlag(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event: "QFocusEvent") -> None:
        """Signal editing end when widget loses focus.

        Args:
            event: Qt focus event.
        """
        self.parentWidget().setEditingFlag(False)
        super().focusOutEvent(event)
