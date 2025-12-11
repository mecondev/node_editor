#!/usr/bin/env python
"""
Main entry point for Node Editor application.

This demonstrates a basic node editor window.
For a full implementation with custom nodes, see examples/example_calculator/

Author: Michael Economou
Date: 2025-12-11
"""

import os
import sys

from PyQt5.QtWidgets import QApplication

from config import APP_NAME, STYLESHEET_PATH, WINDOW_TITLE
from node_editor.utils.qt_helpers import loadStylesheet
from node_editor.widgets.editor_window import NodeEditorWindow


class SimpleNodeEditorWindow(NodeEditorWindow):
    """Basic node editor window."""

    def initUI(self):
        """Initialize the user interface."""
        self.name_company = ""
        self.name_product = APP_NAME

        # Call parent to create basic UI with nodeeditor widget
        super().initUI()

        # Load stylesheet
        stylesheet_path = os.path.join(os.path.dirname(__file__), STYLESHEET_PATH)
        if os.path.exists(stylesheet_path):
            loadStylesheet(stylesheet_path)

        self.setWindowTitle(WINDOW_TITLE)
        self.statusBar().showMessage("Ready")

        # Add some demo nodes
        # TODO: Implement demo nodes for the refactored structure
        # self.node_editor.addNodes()


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Create and show main window
    print(f"Starting {APP_NAME}...")  # noqa: T201
    window = SimpleNodeEditorWindow()
    window.show()
    print(f"{APP_NAME} window opened successfully!")  # noqa: T201

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
