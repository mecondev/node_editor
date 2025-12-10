"""
Theme Engine - Manages theme loading and switching.

Usage:
    from node_editor.themes import ThemeEngine

    ThemeEngine.set_theme("dark")
    theme = ThemeEngine.get_theme()
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QApplication

if TYPE_CHECKING:
    from node_editor.themes.base_theme import BaseTheme


class ThemeEngine:
    """Manages theme loading and switching for the node editor."""

    _current_theme: BaseTheme | None = None
    _themes: dict[str, type[BaseTheme]] = {}

    @classmethod
    def register_theme(cls, theme_class: type[BaseTheme]) -> None:
        """Register a theme class.

        Args:
            theme_class: A theme class that inherits from BaseTheme
        """
        cls._themes[theme_class.name] = theme_class

    @classmethod
    def get_theme(cls, name: str | None = None) -> BaseTheme | None:
        """Get current theme or theme by name.

        Args:
            name: Theme name. If None, returns current theme.

        Returns:
            Theme instance or None if not found
        """
        if name:
            theme_class = cls._themes.get(name)
            return theme_class() if theme_class else None
        return cls._current_theme

    @classmethod
    def set_theme(cls, name: str) -> None:
        """Set the current theme and apply it.

        Args:
            name: Name of the theme to activate

        Raises:
            ValueError: If theme is not registered
        """
        if name not in cls._themes:
            available = ", ".join(cls._themes.keys())
            raise ValueError(f"Theme '{name}' not registered. Available: {available}")

        theme_class = cls._themes[name]
        cls._current_theme = theme_class()
        cls._apply_stylesheet(name)

    @classmethod
    def _apply_stylesheet(cls, theme_name: str) -> None:
        """Load and apply the QSS stylesheet for a theme."""
        theme_dir = os.path.dirname(__file__)
        qss_path = os.path.join(theme_dir, theme_name, "style.qss")

        if os.path.exists(qss_path):
            file = QFile(qss_path)
            file.open(QFile.ReadOnly | QFile.Text)
            stylesheet = str(file.readAll(), encoding="utf-8")
            app = QApplication.instance()
            if app:
                app.setStyleSheet(stylesheet)

    @classmethod
    def available_themes(cls) -> list:
        """Return list of available theme names."""
        return list(cls._themes.keys())

    @classmethod
    def reload_theme(cls) -> None:
        """Reload the current theme (useful after editing QSS)."""
        if cls._current_theme:
            cls.set_theme(cls._current_theme.name)
