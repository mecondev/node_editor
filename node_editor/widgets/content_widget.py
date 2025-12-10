"""Base class for node content widgets."""

from collections import OrderedDict
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from node_editor.core.serializable import Serializable

if TYPE_CHECKING:
    from PyQt5.QtGui import QFocusEvent

    from node_editor.core.node import Node


class QDMNodeContentWidget(QWidget, Serializable):
    """Base class for node's graphics content.

    Provides layout and container for widgets inside a Node.
    Subclass this to create custom node content.

    Attributes:
        node: Reference to the parent Node
        layout: QVBoxLayout container for widgets
    """

    def __init__(self, node: "Node", parent: QWidget | None = None):
        """Initialize content widget.

        Args:
            node: Reference to parent Node
            parent: Parent widget
        """
        self.node = node
        super().__init__(parent)

        self.initUI()

    def initUI(self) -> None:
        """Set up layouts and widgets.

        Override this method to customize node content.
        Default implementation creates a simple label and text edit.
        """
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.wdg_label = QLabel("Some Title")
        self.layout.addWidget(self.wdg_label)
        self.layout.addWidget(QDMTextEdit("foo"))

    def setEditingFlag(self, value: bool) -> None:
        """Set editing flag in graphics view.

        Helper to handle keyboard events in widgets like QLineEdit or QTextEdit.
        Call this when starting/ending editing to prevent view shortcuts from
        triggering while typing.

        Args:
            value: True when starting editing, False when done
        """
        self.node.scene.getView().editingFlag = value

    def serialize(self) -> OrderedDict:
        """Serialize content widget.

        Override to save custom widget state.

        Returns:
            OrderedDict with widget data
        """
        return OrderedDict([])

    def deserialize(
        self, data: dict, hashmap: dict | None = None, restore_id: bool = True
    ) -> bool:
        """Deserialize content widget.

        Override to restore custom widget state.

        Args:
            data: Dictionary with widget data
            hashmap: Map of IDs to objects
            restore_id: Whether to restore the ID

        Returns:
            True if successful
        """
        return True


class QDMTextEdit(QTextEdit):
    """QTextEdit that notifies parent about editing state.

    Example of QTextEdit modification that handles editing state
    by notifying parent QDMNodeContentWidget.
    """

    def focusInEvent(self, event: "QFocusEvent") -> None:
        """Mark start of editing when focused.

        Args:
            event: Qt's focus event
        """
        self.parentWidget().setEditingFlag(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event: "QFocusEvent") -> None:
        """Mark end of editing when focus lost.

        Args:
            event: Qt's focus event
        """
        self.parentWidget().setEditingFlag(False)
        super().focusOutEvent(event)
