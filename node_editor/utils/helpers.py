"""
Helper functions (non-Qt utilities).

Author: Michael Economou
Date: 2025-12-11
"""

import traceback
from pprint import PrettyPrinter


def dumpException(_e: Exception | None = None) -> None:
    """Print an exception with traceback to console.

    Args:
        e: Exception to print (unused, traceback is always printed)
    """
    traceback.print_exc()


pp = PrettyPrinter(indent=4).pprint

# Alias for backwards compatibility
dump_exception = dumpException
