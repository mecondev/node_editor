"""
Node Editor Window - Main application window.

This module provides the NodeEditorWindow class which creates a complete
QMainWindow with menus, actions, and a NodeEditorWidget.
"""

from __future__ import annotations

import json
import os

from PyQt5.QtCore import QPoint, QSettings, QSize
from PyQt5.QtWidgets import QAction, QApplication, QFileDialog, QLabel, QMainWindow, QMessageBox

from node_editor.widgets.editor_widget import NodeEditorWidget


class NodeEditorWindow(QMainWindow):
    """Main window for the node editor application.

    This window provides a complete application interface with:
    - File menu (New, Open, Save, Save As, Exit)
    - Edit menu (Undo, Redo, Cut, Copy, Paste, Delete)
    - Status bar with mouse position
    - Window title with filename
    - Settings persistence

    Attributes:
        NodeEditorWidget_class: Class to use for the central widget
        nodeeditor: NodeEditorWidget instance
        name_company: Company name for settings (default: "oncut")
        name_product: Product name for settings (default: "NodeEditor")
    """

    NodeEditorWidget_class = NodeEditorWidget

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()

        self.name_company = 'oncut'
        self.name_product = 'NodeEditor'

        self.initUI()

    def initUI(self) -> None:
        """Set up the main window with widgets, actions, and menus."""
        self.createActions()
        self.createMenus()

        # Create central widget
        self.nodeeditor = self.__class__.NodeEditorWidget_class(self)
        self.nodeeditor.scene.addHasBeenModifiedListener(self.setTitle)
        self.setCentralWidget(self.nodeeditor)

        self.createStatusBar()

        # Set window properties
        self.setTitle()
        self.show()

    def sizeHint(self) -> QSize:
        """Get the recommended window size.

        Returns:
            QSize(800, 600)
        """
        return QSize(800, 600)

    def createStatusBar(self) -> None:
        """Create the status bar with mouse position display."""
        self.statusBar().showMessage("")
        self.status_mouse_pos = QLabel("")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        self.nodeeditor.view.scenePosChanged.connect(self.onScenePosChanged)

    def createActions(self) -> None:
        """Create File and Edit menu actions."""
        # File actions
        self.actNew = QAction(
            '&New', self, shortcut='Ctrl+N',
            statusTip="Create new graph", triggered=self.onFileNew
        )
        self.actOpen = QAction(
            '&Open', self, shortcut='Ctrl+O',
            statusTip="Open file", triggered=self.onFileOpen
        )
        self.actSave = QAction(
            '&Save', self, shortcut='Ctrl+S',
            statusTip="Save file", triggered=self.onFileSave
        )
        self.actSaveAs = QAction(
            'Save &As...', self, shortcut='Ctrl+Shift+S',
            statusTip="Save file as...", triggered=self.onFileSaveAs
        )
        self.actExit = QAction(
            'E&xit', self, shortcut='Ctrl+Q',
            statusTip="Exit application", triggered=self.close
        )

        # Edit actions
        self.actUndo = QAction(
            '&Undo', self, shortcut='Ctrl+Z',
            statusTip="Undo last operation", triggered=self.onEditUndo
        )
        self.actRedo = QAction(
            '&Redo', self, shortcut='Ctrl+Shift+Z',
            statusTip="Redo last operation", triggered=self.onEditRedo
        )
        self.actCut = QAction(
            'Cu&t', self, shortcut='Ctrl+X',
            statusTip="Cut to clipboard", triggered=self.onEditCut
        )
        self.actCopy = QAction(
            '&Copy', self, shortcut='Ctrl+C',
            statusTip="Copy to clipboard", triggered=self.onEditCopy
        )
        self.actPaste = QAction(
            '&Paste', self, shortcut='Ctrl+V',
            statusTip="Paste from clipboard", triggered=self.onEditPaste
        )
        self.actDelete = QAction(
            '&Delete', self, shortcut='Del',
            statusTip="Delete selected items", triggered=self.onEditDelete
        )

    def createMenus(self) -> None:
        """Create File and Edit menus."""
        self.createFileMenu()
        self.createEditMenu()

    def createFileMenu(self) -> None:
        """Create the File menu."""
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(self.actNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actOpen)
        self.fileMenu.addAction(self.actSave)
        self.fileMenu.addAction(self.actSaveAs)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)

    def createEditMenu(self) -> None:
        """Create the Edit menu."""
        menubar = self.menuBar()
        self.editMenu = menubar.addMenu('&Edit')
        self.editMenu.addAction(self.actUndo)
        self.editMenu.addAction(self.actRedo)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actCut)
        self.editMenu.addAction(self.actCopy)
        self.editMenu.addAction(self.actPaste)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actDelete)

    def setTitle(self) -> None:
        """Update the window title with current filename."""
        title = "Node Editor - "
        title += self.getCurrentNodeEditorWidget().getUserFriendlyFilename()
        self.setWindowTitle(title)

    def closeEvent(self, event) -> None:
        """Handle window close event.

        Args:
            event: Close event
        """
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    # State queries

    def isModified(self) -> bool:
        """Check if the current scene has been modified.

        Returns:
            True if modified
        """
        nodeeditor = self.getCurrentNodeEditorWidget()
        return nodeeditor.scene.isModified() if nodeeditor else False

    def getCurrentNodeEditorWidget(self) -> NodeEditorWidget:
        """Get the current node editor widget.

        Returns:
            NodeEditorWidget instance
        """
        return self.centralWidget()

    def maybeSave(self) -> bool:
        """Ask to save if modified.

        Returns:
            True if we can continue (saved or discarded), False to cancel
        """
        if not self.isModified():
            return True

        res = QMessageBox.warning(
            self, "About to lose your work?",
            "The document has been modified.\n Do you want to save your changes?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )

        if res == QMessageBox.Save:
            return self.onFileSave()
        elif res == QMessageBox.Cancel:
            return False

        return True

    # Event handlers

    def onScenePosChanged(self, x: int, y: int) -> None:
        """Handle scene position change event.

        Args:
            x: New X position
            y: New Y position
        """
        self.status_mouse_pos.setText(f"Scene Pos: [{x}, {y}]")

    # File dialog helpers

    def getFileDialogDirectory(self) -> str:
        """Get starting directory for file dialogs.

        Returns:
            Directory path (empty for default)
        """
        return ''

    def getFileDialogFilter(self) -> str:
        """Get file filter for file dialogs.

        Returns:
            Filter string
        """
        return 'Graph (*.json);;All files (*)'

    # File operations

    def onFileNew(self) -> None:
        """Handle File > New action."""
        if self.maybeSave():
            self.getCurrentNodeEditorWidget().fileNew()
            self.setTitle()

    def onFileOpen(self) -> None:
        """Handle File > Open action."""
        if self.maybeSave():
            fname, filter = QFileDialog.getOpenFileName(
                self, 'Open graph from file',
                self.getFileDialogDirectory(),
                self.getFileDialogFilter()
            )
            if fname != '' and os.path.isfile(fname):
                self.getCurrentNodeEditorWidget().fileLoad(fname)
                self.setTitle()

    def onFileSave(self) -> bool:
        """Handle File > Save action.

        Returns:
            True if saved successfully
        """
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            if not current_nodeeditor.isFilenameSet():
                return self.onFileSaveAs()

            current_nodeeditor.fileSave()
            self.statusBar().showMessage(
                f"Successfully saved {current_nodeeditor.filename}", 5000
            )

            # Support for MDI app
            if hasattr(current_nodeeditor, "setTitle"):
                current_nodeeditor.setTitle()
            else:
                self.setTitle()

            return True

        return False

    def onFileSaveAs(self) -> bool:
        """Handle File > Save As action.

        Returns:
            True if saved successfully
        """
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            fname, filter = QFileDialog.getSaveFileName(
                self, 'Save graph to file',
                self.getFileDialogDirectory(),
                self.getFileDialogFilter()
            )
            if fname == '':
                return False

            self.onBeforeSaveAs(current_nodeeditor, fname)
            current_nodeeditor.fileSave(fname)
            self.statusBar().showMessage(
                f"Successfully saved as {current_nodeeditor.filename}", 5000
            )

            # Support for MDI app
            if hasattr(current_nodeeditor, "setTitle"):
                current_nodeeditor.setTitle()
            else:
                self.setTitle()

            return True

        return False

    def onBeforeSaveAs(self, current_nodeeditor: NodeEditorWidget, filename: str) -> None:
        """Event triggered before saving with a new filename.

        Args:
            current_nodeeditor: NodeEditorWidget being saved
            filename: New filename
        """

    # Edit operations

    def onEditUndo(self) -> None:
        """Handle Edit > Undo action."""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.undo()

    def onEditRedo(self) -> None:
        """Handle Edit > Redo action."""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.redo()

    def onEditDelete(self) -> None:
        """Handle Edit > Delete action."""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.getView().deleteSelected()

    def onEditCut(self) -> None:
        """Handle Edit > Cut action."""
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=True)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditCopy(self) -> None:
        """Handle Edit > Copy action."""
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=False)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self) -> None:
        """Handle Edit > Paste action."""
        if self.getCurrentNodeEditorWidget():
            raw_data = QApplication.instance().clipboard().text()

            try:
                data = json.loads(raw_data)
            except ValueError:
                return

            # Check if the json data is correct
            if 'nodes' not in data:
                return

            return self.getCurrentNodeEditorWidget().scene.clipboard.deserializeFromClipboard(data)

    # Settings persistence

    def readSettings(self) -> None:
        """Read persistent window settings."""
        settings = QSettings(self.name_company, self.name_product)
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self) -> None:
        """Write persistent window settings."""
        settings = QSettings(self.name_company, self.name_product)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
