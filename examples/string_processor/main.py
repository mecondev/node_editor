"""String Processor Node Editor - Main Entry Point.

This example demonstrates string manipulation operations using
the node editor framework.

Author: Michael Economou
Date: 2025-12-14
"""

import logging
import os
import sys

from PyQt5.QtWidgets import QApplication

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from examples.string_processor.str_window import StringProcessorWindow
from node_editor.utils.logging_config import setup_logging

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    setup_logging()
    logger.info("Starting String Processor Example")

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    wnd = StringProcessorWindow()
    wnd.show()
    logger.info("String Processor window opened")

    exit_code = app.exec_()
    logger.info("String Processor exiting with code %d", exit_code)
    sys.exit(exit_code)
