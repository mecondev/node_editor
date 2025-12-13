#!/usr/bin/env python3
"""Quick test script to verify theme system changes."""

import sys

from PyQt5.QtWidgets import QApplication

from node_editor.nodes.input_node import NumberInputNode
from node_editor.nodes.math_nodes import AddNode
from node_editor.themes.theme_engine import ThemeEngine


def test_theme_system() -> None:
    """Test theme registration, switching and refresh."""
    # Check both themes are registered
    available_themes = ThemeEngine.available_themes()
    assert "dark" in available_themes, "Dark theme not registered!"
    assert "light" in available_themes, "Light theme not registered!"

    # Check default theme
    current = ThemeEngine.current_theme()
    assert current.__class__.__name__ == "DarkTheme"

    # Test theme switching
    ThemeEngine.set_theme("light")
    current = ThemeEngine.current_theme()
    assert current.__class__.__name__ == "LightTheme"

    # Switch back
    ThemeEngine.set_theme("dark")
    current = ThemeEngine.current_theme()
    assert current.__class__.__name__ == "DarkTheme"


def test_serialization_version() -> None:
    """Test that scene serialization includes version field."""
    from node_editor.core.scene import Scene

    scene = Scene()

    # Add a simple node
    NumberInputNode(scene)

    # Serialize
    data = scene.serialize()

    # Check version field
    assert "version" in data, "Version field missing in serialization!"
    assert data["version"] == "1.0.0"

    # Deserialize
    scene2 = Scene()
    scene2.deserialize(data)


def test_refresh_graphics_items() -> None:
    """Test refresh_graphics_items method exists and works."""
    from node_editor.core.scene import Scene

    scene = Scene()

    # Create some nodes
    AddNode(scene)
    AddNode(scene)

    # Test refresh method exists
    assert hasattr(
        ThemeEngine, "refresh_graphics_items"
    ), "refresh_graphics_items method missing!"

    # Call it (should not raise)
    ThemeEngine.refresh_graphics_items(scene)


def test_public_api() -> None:
    """Test that public API exports the expected classes."""
    import node_editor

    # Check Scene is exported
    assert hasattr(node_editor, "Scene"), "Scene not exported in public API!"

    # Check themes are exported
    assert hasattr(node_editor, "DarkTheme"), "DarkTheme not exported!"
    assert hasattr(node_editor, "LightTheme"), "LightTheme not exported!"


if __name__ == "__main__":
    # Create QApplication (needed for Qt classes)
    app = QApplication(sys.argv)

    try:
        test_theme_system()
        test_serialization_version()
        test_refresh_graphics_items()
        test_public_api()
        sys.exit(0)
    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)
