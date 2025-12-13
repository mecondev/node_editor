#!/usr/bin/env python
"""Main entry point for the Node Editor application.

This module provides a simple demonstration window for the node editor
framework. It creates a basic editor with sample nodes to showcase
the framework's capabilities.

For a full implementation with custom nodes, see:
    examples/example_calculator/

Example:
    Run the application from the command line::

        $ python main.py

Author:
    Michael Economou

Date:
    2025-12-11
"""

import logging
import os
import sys

from PyQt5.QtWidgets import QApplication

from config import APP_NAME, STYLESHEET_PATH, WINDOW_TITLE
from node_editor.core.node import Node
from node_editor.utils.logging_config import setup_logging
from node_editor.utils.qt_helpers import loadStylesheet
from node_editor.widgets.editor_window import NodeEditorWindow

logger = logging.getLogger(__name__)


class SimpleNodeEditorWindow(NodeEditorWindow):
    """Basic demonstration window for the node editor framework.

    Creates a simple editor window with sample nodes to demonstrate
    the core functionality. Extends NodeEditorWindow with custom
    initialization and demo content.

    Attributes:
        name_company: Company name for settings storage.
        name_product: Product name for settings storage.
    """

    def init_ui(self) -> None:
        """Initialize user interface and add demo content.

        Sets up the main window with stylesheet, title, and status bar.
        Creates sample nodes to demonstrate the editor capabilities.
        """
        self.name_company = ""
        self.name_product = APP_NAME

        super().init_ui()

        stylesheet_path = os.path.join(os.path.dirname(__file__), STYLESHEET_PATH)
        if os.path.exists(stylesheet_path):
            loadStylesheet(stylesheet_path)
            logger.debug("Loaded stylesheet from %s", stylesheet_path)
        else:
            logger.warning("Stylesheet not found: %s", stylesheet_path)

        self.setWindowTitle(WINDOW_TITLE)
        self.statusBar().showMessage("Ready")

        self._create_demo_nodes()

    def _create_demo_nodes(self) -> None:
        """Create sample nodes to demonstrate editor functionality.

        Adds three interconnected nodes at different positions to
        showcase node creation, positioning, and basic layout.
        """
        scene = self.nodeeditor.scene

        try:
            node1 = Node(scene, "Input Node", inputs=[], outputs=[1])
            node1.set_pos(-250, -100)

            node2 = Node(scene, "Process Node", inputs=[1, 1], outputs=[1])
            node2.set_pos(0, -50)

            node3 = Node(scene, "Output Node", inputs=[1], outputs=[])
            node3.set_pos(250, -100)

            logger.info("Created %d demo nodes", 3)
            self.statusBar().showMessage("Demo nodes created - drag to connect!")

        except Exception as e:
            logger.error("Failed to create demo nodes: %s", e)
            self.statusBar().showMessage("Failed to create demo nodes")


def main() -> int:
    """Run the Node Editor application.

    Initializes logging, creates the Qt application, and shows
    the main window. Blocks until the application exits.

    Returns:
        Application exit code (0 for success).
    """
    setup_logging()
    logger.info("Starting %s", APP_NAME)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = SimpleNodeEditorWindow()
    window.show()
    logger.info("Main window opened successfully")

    exit_code = app.exec_()
    logger.info("Application exiting with code %d", exit_code)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
