#!/usr/bin/env python
"""Pytest configuration for node_editor tests.

Provides fixtures and configuration for Qt-based testing.

Author:
    Michael Economou

Date:
    2025-12-12
"""
import pytest  # type: ignore[import-untyped]
from PyQt5.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for Qt tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit - pytest-qt handles this


@pytest.fixture
def scene(qapp):  # noqa: ARG001
    """Create a fresh scene for each test with QApplication available."""
    from node_editor.core.scene import Scene

    return Scene()


@pytest.fixture
def _qtbot(qtbot):
    """Alias for qtbot that can be used as unused param (_qtbot)."""
    return qtbot
