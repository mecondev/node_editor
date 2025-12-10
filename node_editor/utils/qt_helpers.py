"""Qt-specific helper functions."""

from PyQt5.QtCore import QFile, Qt
from PyQt5.QtWidgets import QApplication


def loadStylesheet(filename: str) -> None:
    """Load a QSS stylesheet to the current QApplication.
    
    Args:
        filename: Path to the QSS stylesheet file
    """
    print(f"Loading stylesheet: {filename}")
    file = QFile(filename)
    if not file.open(QFile.ReadOnly | QFile.Text):
        print(f"Warning: Could not open stylesheet: {filename}")
        return
        
    stylesheet = file.readAll()
    app = QApplication.instance()
    if app:
        app.setStyleSheet(str(stylesheet, encoding="utf-8"))


def loadStylesheets(*filenames: str) -> None:
    """Load and concatenate multiple QSS stylesheets.
    
    Args:
        *filenames: Variable number of stylesheet file paths
    """
    combined = ""
    for filename in filenames:
        file = QFile(filename)
        if not file.open(QFile.ReadOnly | QFile.Text):
            print(f"Warning: Could not open stylesheet: {filename}")
            continue
        stylesheet = file.readAll()
        combined += "\n" + str(stylesheet, encoding="utf-8")
    
    app = QApplication.instance()
    if app:
        app.setStyleSheet(combined)


def isCTRLPressed(event) -> bool:
    """Check if CTRL/CMD key is pressed.
    
    Args:
        event: Qt event object
        
    Returns:
        True if Control modifier is pressed
    """
    return bool(event.modifiers() & Qt.ControlModifier)


def isSHIFTPressed(event) -> bool:
    """Check if SHIFT key is pressed.
    
    Args:
        event: Qt event object
        
    Returns:
        True if Shift modifier is pressed
    """
    return bool(event.modifiers() & Qt.ShiftModifier)


def isALTPressed(event) -> bool:
    """Check if ALT key is pressed.
    
    Args:
        event: Qt event object
        
    Returns:
        True if Alt modifier is pressed
    """
    return bool(event.modifiers() & Qt.AltModifier)
