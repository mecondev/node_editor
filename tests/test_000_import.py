#!/usr/bin/env python
"""Basic import tests for the node_editor package.

Verifies that core module imports work correctly.

Author:
    Michael Economou

Date:
    2025-12-11
"""


import unittest

from node_editor.core.scene import Scene


class TestTemplate(unittest.TestCase):
    """Basic tests for node_editor package imports."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test if Scene has has_been_modified property."""
        assert hasattr(Scene, "has_been_modified")
