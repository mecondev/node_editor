"""String Processor - Main Window.

Main window for string processor node editor with single canvas (no MDI).

Author: Michael Economou
Date: 2025-12-14
"""

import logging
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QAction, QDockWidget, QFileDialog, QMessageBox

from examples.string_processor.str_drag_listbox import StrDragListbox
from examples.string_processor.str_sub_window import StrSubWindow
from node_editor.core.edge import Edge
from node_editor.tools.edge_validators import (
    edge_cannot_connect_input_and_output_of_same_node,
    edge_cannot_connect_two_outputs_or_two_inputs,
)
from node_editor.utils.qt_helpers import loadStylesheets
from node_editor.widgets.editor_window import NodeEditorWindow

# Register edge validators
Edge.register_edge_validator(edge_cannot_connect_two_outputs_or_two_inputs)
Edge.register_edge_validator(edge_cannot_connect_input_and_output_of_same_node)

logger = logging.getLogger(__name__)


class StringProcessorWindow(NodeEditorWindow):
    """Main window for string processor node editor."""

    def init_ui(self):
        """Initialize the user interface."""
        self.name_company = 'oncut'
        self.name_product = 'String Processor Node Editor'

        self.stylesheet_filename = os.path.join(os.path.dirname(__file__), "qss/nodeeditor.qss")
        loadStylesheets(
            os.path.join(os.path.dirname(__file__), "qss/nodeeditor-dark.qss"),
            self.stylesheet_filename
        )

        self.empty_icon = QIcon(".")

        # Create central widget (single canvas)
        self.nodeeditor = StrSubWindow()
        self.setCentralWidget(self.nodeeditor)

        self.create_nodes_dock()
        self.create_actions()
        self.create_menus()
        self.create_tool_bars()
        self.create_status_bar()
        self.update_menus()

        self.read_settings()

        self.setWindowTitle("String Processor Node Editor")

        # Load example file if exists
        self.load_initial_file()

    def load_initial_file(self):
        """Load the example file on startup if it exists."""
        example_file = os.path.join(os.path.dirname(__file__), "string_example.json")
        if os.path.exists(example_file):
            try:
                self.nodeeditor.file_load(example_file)
                self.statusBar().showMessage(f"Loaded example: {example_file}", 5000)
            except Exception as e:
                logger.error("Failed to load example file: %s", e)

    def closeEvent(self, event):
        """Handle window close event."""
        if self.maybe_save():
            self.write_settings()
            event.accept()
        else:
            event.ignore()

    def create_actions(self):
        """Create actions for menus and toolbars."""
        super().create_actions()

        self.actNew = QAction(
            "&New", self,
            shortcut=QKeySequence.New,
            statusTip="Create new graph",
            triggered=self.on_file_new
        )

        self.actAbout = QAction(
            "&About", self,
            statusTip="Show the application's About box",
            triggered=self.about
        )

    def on_file_new(self):
        """Handle File > New action."""
        if self.maybe_save():
            self.nodeeditor.scene.clear()
            self.nodeeditor.filename = None
            self.nodeeditor.setTitle()
            self.statusBar().showMessage("New file created", 5000)

    def maybe_save(self):
        """Ask user to save if there are unsaved changes.

        Returns:
            bool: True if it's safe to proceed, False if cancelled.
        """
        if not self.nodeeditor.scene.has_been_modified:
            return True

        result = QMessageBox.question(
            self,
            "Unsaved Changes",
            "The document has been modified.\nDo you want to save your changes?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )

        if result == QMessageBox.Save:
            return self.on_file_save()
        elif result == QMessageBox.Cancel:
            return False

        return True

    def on_file_open(self):
        """Handle File > Open action."""
        if self.maybe_save():
            fname, _ = QFileDialog.getOpenFileName(
                self,
                "Open graph from file",
                self.get_file_dialog_directory(),
                self.get_file_dialog_filter()
            )
            if fname:
                if os.path.isfile(fname):
                    self.nodeeditor.file_load(fname)

    def on_file_save(self):
        """Handle File > Save action."""
        if self.nodeeditor.filename is None:
            return self.on_file_save_as()

        self.nodeeditor.file_save()
        self.statusBar().showMessage(f"Saved to {self.nodeeditor.filename}", 5000)
        return True

    def on_file_save_as(self):
        """Handle File > Save As action."""
        fname, _ = QFileDialog.getSaveFileName(
            self,
            "Save graph to file",
            self.get_file_dialog_directory(),
            self.get_file_dialog_filter()
        )

        if fname == '':
            return False

        self.nodeeditor.file_save(fname)
        self.statusBar().showMessage(f"Saved to {fname}", 5000)
        return True

    def create_nodes_dock(self):
        """Create the nodes dock widget."""
        self.nodes_dock = QDockWidget("Nodes")
        self.nodes_dock.setWidget(StrDragListbox())
        self.nodes_dock.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.nodes_dock)

    def create_tool_bars(self):
        """Create tool bars (empty for now)."""

    def create_menus(self):
        """Create menus."""
        super().create_menus()
        self.createFileMenu()
        self.createEditMenu()
        self.createHelpMenu()

    def createFileMenu(self):
        """Create File menu."""
        menu_bar = self.menuBar()
        self.fileMenu = menu_bar.addMenu("&File")
        self.fileMenu.addAction(self.actNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actOpen)
        self.fileMenu.addAction(self.actSave)
        self.fileMenu.addAction(self.actSaveAs)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)

    def createEditMenu(self):
        """Create Edit menu."""
        menu_bar = self.menuBar()
        self.editMenu = menu_bar.addMenu("&Edit")
        self.editMenu.addAction(self.actUndo)
        self.editMenu.addAction(self.actRedo)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actCut)
        self.editMenu.addAction(self.actCopy)
        self.editMenu.addAction(self.actPaste)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actDelete)

    def createHelpMenu(self):
        """Create Help menu."""
        menu_bar = self.menuBar()
        self.helpMenu = menu_bar.addMenu("&Help")
        self.helpMenu.addAction(self.actAbout)

    def get_current_node_editor_widget(self):
        """Get the current node editor widget."""
        return self.nodeeditor

    def update_menus(self):
        """Update menu states."""
        active = self.get_current_node_editor_widget()
        has_selection = active is not None

        self.actPaste.setEnabled(has_selection)
        self.actCut.setEnabled(has_selection)
        self.actCopy.setEnabled(has_selection)

    def get_file_dialog_directory(self):
        """Get directory for file dialogs."""
        return os.path.dirname(__file__)

    def get_file_dialog_filter(self):
        """Get file filter for dialogs."""
        return "Graph files (*.json);;All files (*)"

    def about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About String Processor",
            "String Processor Node Editor\n\n"
            "A visual programming environment for string manipulation.\n\n"
            "Built with PyQt Node Editor Framework"
        )
