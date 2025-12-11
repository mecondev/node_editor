"""
Utils module - Helper functions and utilities.

Functions:
    - loadStylesheet: Load a QSS stylesheet
    - loadStylesheets: Load multiple stylesheets
    - dumpException: Debug helper for exceptions
    - pp: Pretty print
    - setup_logging: Configure logging for the application
    - get_logger: Get a logger for a module

Author: Michael Economou
Date: 2025-12-11
"""

from node_editor.utils.helpers import dumpException, pp
from node_editor.utils.logging_config import get_logger, setup_logging
from node_editor.utils.qt_helpers import (
    isALTPressed,
    isCTRLPressed,
    isSHIFTPressed,
    loadStylesheet,
    loadStylesheets,
)

__all__ = [
    "dumpException",
    "pp",
    "loadStylesheet",
    "loadStylesheets",
    "isCTRLPressed",
    "isSHIFTPressed",
    "isALTPressed",
    "setup_logging",
    "get_logger",
]

