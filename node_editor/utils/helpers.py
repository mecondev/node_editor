"""Helper functions (non-Qt utilities)."""

import traceback
from pprint import PrettyPrinter


def dumpException(e: Exception | None = None) -> None:
    """Print an exception with traceback to console.
    
    Args:
        e: Exception to print (unused, traceback is always printed)
    """
    traceback.print_exc()


pp = PrettyPrinter(indent=4).pprint
