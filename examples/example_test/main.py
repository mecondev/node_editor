"""
Module description.
Author: Michael Economou
Date: 2025-12-11
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
    # NOTE: addNodes() has been removed in refactoring
    # wnd.node_editor.addNodes()
    module_path = os.path.dirname(inspect.getfile(wnd.__class__))

    loadStylesheet(os.path.join(module_path, "qss/nodestyle.qss"))

    sys.exit(app.exec_())
