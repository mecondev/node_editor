"""
Themes module - Theme engine for customizing node editor appearance.

Usage:
    from node_editor.themes import ThemeEngine

    # Set theme
    ThemeEngine.set_theme("dark")

    # Get current theme colors
    theme = ThemeEngine.get_theme()
    color = theme.node_background
"""

from node_editor.themes.base_theme import BaseTheme

# Import and register built-in themes
from node_editor.themes.dark import DarkTheme
from node_editor.themes.light import LightTheme
from node_editor.themes.theme_engine import ThemeEngine

ThemeEngine.register_theme(DarkTheme)
ThemeEngine.register_theme(LightTheme)

# Set dark as default
ThemeEngine.set_theme("dark")

__all__ = [
    "ThemeEngine",
    "BaseTheme",
    "DarkTheme",
    "LightTheme",
]
