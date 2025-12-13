"""Utility functions and helpers for the node editor.

This module provides common utility functions used throughout the
node editor framework, including stylesheet loading, exception handling,
and logging configuration.

Functions:
    loadStylesheet: Load a single QSS stylesheet to QApplication.
    loadStylesheets: Load and concatenate multiple QSS stylesheets.
    isCTRLPressed: Check if Control modifier is active.
    isSHIFTPressed: Check if Shift modifier is active.
    isALTPressed: Check if Alt modifier is active.
     dump_exception: Print exception with traceback for debugging.
    pp: Pretty-print objects to console.
    setup_logging: Configure application-wide logging handlers.
    get_logger: Get a named logger instance.

Author:
    Michael Economou

Date:
    2025-12-11
"""

from node_editor.utils.helpers import dump_exception, pp
from node_editor.utils.logging_config import get_logger, setup_logging
from node_editor.utils.qt_helpers import (
    isALTPressed,
    isCTRLPressed,
    isSHIFTPressed,
    loadStylesheet,
    loadStylesheets,
)

__all__ = [
     "dump_exception",
    "pp",
    "loadStylesheet",
    "loadStylesheets",
    "isCTRLPressed",
    "isSHIFTPressed",
    "isALTPressed",
    "setup_logging",
    "get_logger",
]

