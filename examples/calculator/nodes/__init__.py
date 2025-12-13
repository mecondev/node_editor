"""
Module description.
Author: Michael Economou
Date: 2025-12-11
"""


# __all__ = [ "operations", "input", "output" ]

import glob
from os.path import basename, dirname, isfile, join

modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
