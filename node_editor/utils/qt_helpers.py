"""Qt-specific helper functions for the node editor.

This module provides utility functions that depend on PyQt5,
including stylesheet loading and keyboard modifier detection.

Functions:
    loadStylesheet: Load a single QSS stylesheet.
    loadStylesheets: Load and concatenate multiple QSS stylesheets.
    isCTRLPressed: Check if Control modifier is active.
    isSHIFTPressed: Check if Shift modifier is active.
    isALTPressed: Check if Alt modifier is active.

Author:
    Michael Economou

Date:
    2025-12-11
"""

from PyQt5.QtCore import QFile, Qt
from PyQt5.QtWidgets import QApplication


def loadStylesheet(filename: str) -> None:
    """Load a QSS stylesheet and apply to the application.

    Reads the stylesheet file and sets it as the application's
    global stylesheet, affecting all widgets.

    Args:
        filename: Path to the QSS stylesheet file.
    """
    file = QFile(filename)
    if not file.open(QFile.ReadOnly | QFile.Text):
        return

    stylesheet = file.readAll()
    app = QApplication.instance()
    if app:
        app.setStyleSheet(str(stylesheet, encoding="utf-8"))


def loadStylesheets(*filenames: str) -> None:
    """Load and combine multiple QSS stylesheets.

    Reads multiple stylesheet files, concatenates their contents,
    and applies the combined stylesheet to the application.

    Args:
        *filenames: Paths to QSS stylesheet files.
    """
    combined = ""
    for filename in filenames:
        file = QFile(filename)
        if not file.open(QFile.ReadOnly | QFile.Text):
            continue
        stylesheet = file.readAll()
        combined += "\n" + str(stylesheet, encoding="utf-8")

    app = QApplication.instance()
    if app:
        app.setStyleSheet(combined)


def isCTRLPressed(event) -> bool:
    """Check if Control (or Command on Mac) is pressed.

    Args:
        event: Qt event with modifiers() method.

    Returns:
        True if Control modifier is active.
    """
    return bool(event.modifiers() & Qt.ControlModifier)


def isSHIFTPressed(event) -> bool:
    """Check if Shift key is pressed.

    Args:
        event: Qt event with modifiers() method.

    Returns:
        True if Shift modifier is active.
    """
    return bool(event.modifiers() & Qt.ShiftModifier)


def isALTPressed(event) -> bool:
    """Check if Alt key is pressed.

    Args:
        event: Qt event with modifiers() method.

    Returns:
        True if Alt modifier is active.
    """
    return bool(event.modifiers() & Qt.AltModifier)


# Snake_case aliases for consistency
is_ctrl_pressed = isCTRLPressed
is_shift_pressed = isSHIFTPressed
is_alt_pressed = isALTPressed
