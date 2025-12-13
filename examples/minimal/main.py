"""Minimal example demonstrating basic node editor usage.

This is the simplest possible example showing how to create
a NodeEditorWindow with default configuration.

The example demonstrates:
    - Creating a standalone NodeEditorWindow
    - Loading a QSS stylesheet for visual styling
    - Basic application setup with QApplication

This serves as a starting point for custom applications.
For more advanced features, see examples/calculator/.

Example:
    Run from command line::

        $ python examples/minimal/main.py

Author:
    Michael Economou

Date:
    2025-12-11
"""
import inspect
import os
import sys

from PyQt5.QtWidgets import QApplication

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from node_editor.utils.qt_helpers import loadStylesheet
from node_editor.widgets.editor_window import NodeEditorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    wnd = NodeEditorWindow()
    module_path = os.path.dirname(inspect.getfile(wnd.__class__))

    loadStylesheet(os.path.join(module_path, "qss/nodestyle.qss"))

    wnd.show()  # Show the window
    sys.exit(app.exec_())
