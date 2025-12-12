"""Node editor widget combining scene and view into embeddable canvas.

This module provides NodeEditorWidget, a complete node editing interface
that can be embedded in applications. It combines Scene and QDMGraphicsView
with file operations and state management.

The widget handles:
    - Scene creation and management
    - File load/save operations
    - Undo/redo state queries
    - Selection management

Author:
    Michael Economou

Date:
    2025-12-11
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QVBoxLayout, QWidget

from node_editor.core.scene import InvalidFileError, Scene
from node_editor.utils.helpers import dump_exception

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QGraphicsItem


class NodeEditorWidget(QWidget):
    """Embeddable node editor canvas widget.

    Combines Scene and QDMGraphicsView into a single widget for
    embedding in applications. Provides file operations and
    state management.

    Attributes:
        Scene_class: Scene class to instantiate.
        GraphicsView_class: View class to instantiate.
        scene: Active Scene instance.
        view: Active QDMGraphicsView instance.
        filename: Current file path, or None for unsaved.
    """

    Scene_class = Scene
    GraphicsView_class = None

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize node editor widget.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self.filename: str | None = None

        self.initUI()

    def initUI(self) -> None:
        """Set up layout with scene and view."""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.scene = self.__class__.Scene_class()

        from node_editor.graphics.view import QDMGraphicsView

        if self.__class__.GraphicsView_class is None:
            self.__class__.GraphicsView_class = QDMGraphicsView

        self.view = self.__class__.GraphicsView_class(self.scene.graphics_scene, self)
        self.layout.addWidget(self.view)

    def isModified(self) -> bool:
        """Check if scene has unsaved changes.

        Returns:
            True if scene has been modified.
        """
        return self.scene.isModified()

    def isFilenameSet(self) -> bool:
        """Check if file has been saved.

        Returns:
            True if filename is set, False for new graphs.
        """
        return self.filename is not None

    def getUserFriendlyFilename(self) -> str:
        """Get display name with modification indicator.

        Returns:
            Filename with asterisk if modified, or 'New Graph'.
        """
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Graph"
        return name + ("*" if self.isModified() else "")

    def getSelectedItems(self) -> list[QGraphicsItem]:
        """Get currently selected graphics items.

        Returns:
            List of selected QGraphicsItem instances.
        """
        return self.scene.getSelectedItems()

    def hasSelectedItems(self) -> bool:
        """Check if any items are selected.

        Returns:
            True if selection is non-empty.
        """
        return self.getSelectedItems() != []

    def canUndo(self) -> bool:
        """Check if undo operation is available.

        Returns:
            True if undo stack has entries.
        """
        return self.scene.history.canUndo()

    def canRedo(self) -> bool:
        """Check if redo operation is available.

        Returns:
            True if redo stack has entries.
        """
        return self.scene.history.canRedo()

    def fileNew(self) -> None:
        """Create new empty scene.

        Clears current content and resets history.
        """
        self.scene.clear()
        self.filename = None
        self.scene.history.clear()
        self.scene.history.storeInitialHistoryStamp()

    def fileLoad(self, filename: str) -> bool:
        """Load graph from JSON file.

        Args:
            filename: Path to file to load.

        Returns:
            True if load succeeded, False on error.
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.scene.loadFromFile(filename)
            self.filename = filename
            self.scene.history.clear()
            self.scene.history.storeInitialHistoryStamp()
            return True
        except FileNotFoundError as e:
            dump_exception(e)
            QMessageBox.warning(
                self, f"Error loading {os.path.basename(filename)}", str(e).replace("[Errno 2]", "")
            )
            return False
        except InvalidFileError as e:
            dump_exception(e)
            QMessageBox.warning(self, f"Error loading {os.path.basename(filename)}", str(e))
            return False
        finally:
            QApplication.restoreOverrideCursor()

    def fileSave(self, filename: str | None = None) -> bool:
        """Save graph to JSON file.

        Args:
            filename: Path to save to. Uses current filename if None.

        Returns:
            True if save succeeded.
        """
        if filename is not None:
            self.filename = filename

        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.scene.saveToFile(self.filename)
        QApplication.restoreOverrideCursor()

        return True
