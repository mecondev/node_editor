"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
import logging
import os
import sys

from PyQt5.QtWidgets import QApplication

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from examples.calculator.calc_window import CalculatorWindow
from node_editor.utils.logging_config import setup_logging

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    setup_logging()
    logger.info("Starting Calculator Example")

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    wnd = CalculatorWindow()
    wnd.show()
    logger.info("Calculator window opened")

    exit_code = app.exec_()
    logger.info("Calculator exiting with code %d", exit_code)
    sys.exit(exit_code)
