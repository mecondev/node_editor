"""Main application window for node editor.

This module provides NodeEditorWindow, a complete QMainWindow with
menus, actions, status bar, and settings persistence. It wraps
NodeEditorWidget to provide a ready-to-use application.

Features:
    - File menu: New, Open, Save, Save As, Exit
    - Edit menu: Undo, Redo, Cut, Copy, Paste, Delete
    - Status bar with mouse position display
    - Window title with filename and modification indicator
    - Persistent window geometry settings

Author:
    Michael Economou

Date:
    2025-12-11
"""

from __future__ import annotations

import json
import os

from PyQt5.QtCore import QPoint, QSettings, QSize
from PyQt5.QtWidgets import QAction, QApplication, QFileDialog, QLabel, QMainWindow, QMessageBox

from node_editor.widgets.editor_widget import NodeEditorWidget


class NodeEditorWindow(QMainWindow):
    """Complete application window for node editing.

    Provides full application interface with menus, status bar,
    and settings persistence. Subclass to customize behavior
    or add additional menus.

    Attributes:
        NodeEditorWidget_class: Widget class for central editor.
        nodeeditor: Active NodeEditorWidget instance.
        name_company: Company name for QSettings storage.
        name_product: Product name for QSettings storage.
    """

    NodeEditorWidget_class = NodeEditorWidget

    def __init__(self) -> None:
        """Initialize main window with menus and central widget."""
        super().__init__()

        self.name_company = 'oncut'
        self.name_product = 'NodeEditor'

        self.initUI()

    def initUI(self) -> None:
        """Set up window with actions, menus, and central widget."""
        self.createActions()
        self.createMenus()

        self.nodeeditor = self.__class__.NodeEditorWidget_class(self)
        self.nodeeditor.scene.addHasBeenModifiedListener(self.setTitle)
        self.setCentralWidget(self.nodeeditor)

        self.createStatusBar()

        self.setTitle()
        self.show()

    def sizeHint(self) -> QSize:
        """Get recommended window size.

        Returns:
            QSize with default dimensions.
        """
        return QSize(800, 600)

    def createStatusBar(self) -> None:
        """Set up status bar with mouse position label."""
        self.statusBar().showMessage("")
        self.status_mouse_pos = QLabel("")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        self.nodeeditor.view.scene_pos_changed.connect(self.onScenePosChanged)

    def createActions(self) -> None:
        """Create QAction instances for menus."""
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
        """Populate File menu with actions."""
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
        """Populate Edit menu with actions."""
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
        """Update window title with current filename."""
        title = "Node Editor - "
        title += self.getCurrentNodeEditorWidget().getUserFriendlyFilename()
        self.setWindowTitle(title)

    def closeEvent(self, event) -> None:
        """Prompt to save before closing.

        Args:
            event: Qt close event.
        """
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def isModified(self) -> bool:
        """Check if current scene has unsaved changes.

        Returns:
            True if scene is modified.
        """
        nodeeditor = self.getCurrentNodeEditorWidget()
        return nodeeditor.scene.isModified() if nodeeditor else False

    def getCurrentNodeEditorWidget(self) -> NodeEditorWidget:
        """Get the active node editor widget.

        Returns:
            NodeEditorWidget instance.
        """
        return self.centralWidget()

    def maybeSave(self) -> bool:
        """Prompt user to save if modified.

        Returns:
            True to continue, False to cancel operation.
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

    def onScenePosChanged(self, x: int, y: int) -> None:
        """Update status bar with mouse position.

        Args:
            x: Scene X coordinate.
            y: Scene Y coordinate.
        """
        self.status_mouse_pos.setText(f"Scene Pos: [{x}, {y}]")

    def getFileDialogDirectory(self) -> str:
        """Get starting directory for file dialogs.

        Returns:
            Directory path string.
        """
        return ''

    def getFileDialogFilter(self) -> str:
        """Get file type filter for dialogs.

        Returns:
            Filter string for QFileDialog.
        """
        return 'Graph (*.json);;All files (*)'

    def onFileNew(self) -> None:
        """Create new empty graph after save prompt."""
        if self.maybeSave():
            self.getCurrentNodeEditorWidget().fileNew()
            self.setTitle()

    def onFileOpen(self) -> None:
        """Open file dialog and load selected graph."""
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
        """Save to current file or prompt for filename.

        Returns:
            True if save succeeded.
        """
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            if not current_nodeeditor.isFilenameSet():
                return self.onFileSaveAs()

            current_nodeeditor.fileSave()
            self.statusBar().showMessage(
                f"Successfully saved {current_nodeeditor.filename}", 5000
            )

            if hasattr(current_nodeeditor, "setTitle"):
                current_nodeeditor.setTitle()
            else:
                self.setTitle()

            return True

        return False

    def onFileSaveAs(self) -> bool:
        """Prompt for filename and save graph.

        Returns:
            True if save succeeded.
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

            if hasattr(current_nodeeditor, "setTitle"):
                current_nodeeditor.setTitle()
            else:
                self.setTitle()

            return True

        return False

    def onBeforeSaveAs(self, current_nodeeditor: NodeEditorWidget, filename: str) -> None:
        """Hook called before Save As completes.

        Override to perform actions before saving with new name.

        Args:
            current_nodeeditor: Widget being saved.
            filename: New filename path.
        """

    def onEditUndo(self) -> None:
        """Undo last operation."""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.undo()

    def onEditRedo(self) -> None:
        """Redo last undone operation."""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.redo()

    def onEditDelete(self) -> None:
        """Delete selected items."""
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.getView().deleteSelected()

    def onEditCut(self) -> None:
        """Cut selected items to clipboard."""
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=True)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditCopy(self) -> None:
        """Copy selected items to clipboard."""
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=False)
            str_data = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self) -> None:
        """Paste items from clipboard."""
        if self.getCurrentNodeEditorWidget():
            raw_data = QApplication.instance().clipboard().text()

            try:
                data = json.loads(raw_data)
            except ValueError:
                return

            if 'nodes' not in data:
                return

            return self.getCurrentNodeEditorWidget().scene.clipboard.deserializeFromClipboard(data)

    def readSettings(self) -> None:
        """Restore window geometry from persistent settings."""
        settings = QSettings(self.name_company, self.name_product)
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self) -> None:
        """Save window geometry to persistent settings."""
        settings = QSettings(self.name_company, self.name_product)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
