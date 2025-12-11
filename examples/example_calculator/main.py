"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""
import os
import sys

from PyQt5.QtWidgets import QApplication

sys.path.insert(0, os.path.join( os.path.dirname(__file__), "..", ".." ))

from examples.example_calculator.calc_window import CalculatorWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # print(QStyleFactory.keys())
    app.setStyle('Fusion')

    wnd = CalculatorWindow()
    wnd.show()

    sys.exit(app.exec_())
