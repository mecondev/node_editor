"""General helper functions without Qt dependencies.

This module provides basic utility functions that do not require Qt,
suitable for use in any Python context.

Functions:
    dumpException: Print exception traceback for debugging.
    pp: Pretty-print data structures.

Author:
    Michael Economou

Date:
    2025-12-11
"""

import traceback
from pprint import PrettyPrinter


def dumpException(_e: Exception | None = None) -> None:
    """Print the current exception traceback to console.

    Useful for debugging exception handlers. Prints the full
    traceback of the most recent exception.

    Args:
        _e: Exception instance (unused, current traceback is printed).
    """
    traceback.print_exc()


pp = PrettyPrinter(indent=4).pprint
"""Pretty-print function with 4-space indentation."""

dump_exception = dumpException
"""Alias for backwards compatibility with snake_case naming."""
