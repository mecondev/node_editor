"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
import logging
import os
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from examples.calculator.calc_window import CalculatorWindow
from node_editor.utils.logging_config import setup_logging

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    setup_logging()
    logger.info("Starting Calculator Example")

    app = QApplication(sys.argv)

    # print(QStyleFactory.keys())
    app.setStyle('Fusion')

    wnd = CalculatorWindow()
    wnd.show()
    logger.info("Calculator window opened")

    auto_exit_seconds = os.environ.get("AUTO_EXIT_SECONDS")
    if auto_exit_seconds is not None:
        try:
            delay_ms = int(float(auto_exit_seconds) * 1000)
            QTimer.singleShot(delay_ms, app.quit)
        except ValueError:
            # Ignore invalid env value; run normally
            pass

    exit_code = app.exec_()
    logger.info("Calculator exiting with code %d", exit_code)
    sys.exit(exit_code)
