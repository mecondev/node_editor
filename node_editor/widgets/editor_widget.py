"""
Node Editor Widget - Main widget containing scene and view.

This module provides the NodeEditorWidget class which combines the Scene
and GraphicsView into a single widget that can be embedded in applications.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QMessageBox

from node_editor.core.scene import Scene, InvalidFile
from node_editor.utils.helpers import dump_exception

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QGraphicsItem


class NodeEditorWidget(QWidget):
    """Main widget containing the node editor scene and view.
    
    This widget provides a complete node editor interface that can be embedded
    in other applications. It includes file operations, undo/redo support,
    and scene management.
    
    Attributes:
        Scene_class: Class to use for creating scenes (default: Scene)
        GraphicsView_class: Class to use for creating views (default: QDMGraphicsView)
        scene: Scene instance
        view: QDMGraphicsView instance
        filename: Current file path or None
    """
    
    Scene_class = Scene
    GraphicsView_class = None  # Will be set after imports
    
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the node editor widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.filename: str | None = None
        
        self.initUI()
    
    def initUI(self) -> None:
        """Set up the widget with layout, scene, and view."""
        # Create layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        # Create scene
        self.scene = self.__class__.Scene_class()
        
        # Create view (late import to avoid circular dependencies)
        from node_editor.graphics.view import QDMGraphicsView
        if self.__class__.GraphicsView_class is None:
            self.__class__.GraphicsView_class = QDMGraphicsView
        
        self.view = self.__class__.GraphicsView_class(self.scene.grScene, self)
        self.layout.addWidget(self.view)
    
    # State queries
    
    def isModified(self) -> bool:
        """Check if the scene has been modified.
        
        Returns:
            True if the scene has been modified
        """
        return self.scene.isModified()
    
    def isFilenameSet(self) -> bool:
        """Check if a filename is associated with this graph.
        
        Returns:
            True if filename is set, False for new unsaved graphs
        """
        return self.filename is not None
    
    def getUserFriendlyFilename(self) -> str:
        """Get user-friendly filename for display.
        
        Returns:
            Base filename with asterisk if modified, or "New Graph"
        """
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Graph"
        return name + ("*" if self.isModified() else "")
    
    # Selection
    
    def getSelectedItems(self) -> list[QGraphicsItem]:
        """Get currently selected items in the scene.
        
        Returns:
            List of selected QGraphicsItem instances
        """
        return self.scene.getSelectedItems()
    
    def hasSelectedItems(self) -> bool:
        """Check if any items are selected.
        
        Returns:
            True if something is selected
        """
        return self.getSelectedItems() != []
    
    # Undo/Redo
    
    def canUndo(self) -> bool:
        """Check if undo is available.
        
        Returns:
            True if undo can be performed
        """
        return self.scene.history.canUndo()
    
    def canRedo(self) -> bool:
        """Check if redo is available.
        
        Returns:
            True if redo can be performed
        """
        return self.scene.history.canRedo()
    
    # File operations
    
    def fileNew(self) -> None:
        """Create a new empty scene."""
        self.scene.clear()
        self.filename = None
        self.scene.history.clear()
        self.scene.history.storeInitialHistoryStamp()
    
    def fileLoad(self, filename: str) -> bool:
        """Load a graph from a JSON file.
        
        Args:
            filename: Path to the file to load
            
        Returns:
            True if loading succeeded, False otherwise
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
                self,
                f"Error loading {os.path.basename(filename)}",
                str(e).replace('[Errno 2]', '')
            )
            return False
        except InvalidFile as e:
            dump_exception(e)
            QMessageBox.warning(
                self,
                f"Error loading {os.path.basename(filename)}",
                str(e)
            )
            return False
        finally:
            QApplication.restoreOverrideCursor()
    
    def fileSave(self, filename: str | None = None) -> bool:
        """Save the graph to a JSON file.
        
        Args:
            filename: Path to save to. If None, uses current filename
            
        Returns:
            True if saving succeeded
        """
        if filename is not None:
            self.filename = filename
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.scene.saveToFile(self.filename)
        QApplication.restoreOverrideCursor()
        
        return True
