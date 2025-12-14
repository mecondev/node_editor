#!/usr/bin/env python3
"""Icon Viewer for Node Editor Examples.

This script displays all the Material Design icons selected for the node editor
examples. It creates a visual gallery organized by category.

Usage:
    python scripts/view_icons.py

Author: Michael Economou
Date: 2025-12-14
"""

import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QGroupBox,
    QLabel,
    QMainWindow,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

# Path to Google Material Design icons (outlined)
ICONS_SOURCE_PATH = "/mnt/data_1/edu/Tools/Google_material_design_icons/outlined"

# Icon size for display
ICON_SIZE = 48

# ============================================================================
# ICON MAPPINGS - Selected icons for each node category
# ============================================================================

# Common icons (shared across examples)
COMMON_ICONS = {
    "input.svg": "Input Node (generic)",
    "output.svg": "Output Node (generic)",
    "login.svg": "Input Node (alternative)",
    "logout.svg": "Output Node (alternative)",
}

# Calculator / Math nodes
MATH_ICONS = {
    "add.svg": "Add (+)",
    "remove.svg": "Subtract (-)",
    "close.svg": "Multiply (×)",
    "more_horiz.svg": "Divide (÷)",
    "percent.svg": "Percentage (%)",
    "calculate.svg": "Calculator (general)",
    "functions.svg": "Math Functions",
    "exposure_plus_1.svg": "Power (^)",
    "square_foot.svg": "Square Root (√)",
    "vertical_align_center.svg": "Absolute Value |x|",
    "unfold_less.svg": "Minimum",
    "unfold_more.svg": "Maximum",
    "360.svg": "Round",
    "grid_3x3.svg": "Modulo (mod)",
}

# String processing nodes
STRING_ICONS = {
    "text_fields.svg": "Text Input",
    "output.svg": "Text Output",
    "link.svg": "Concatenate (join strings)",
    "data_object.svg": "Format (template {})",
    "tag.svg": "String Length (#)",
    "content_cut.svg": "Substring (slice)",
    "call_split.svg": "Split (to list)",
    "uppercase.svg": "Uppercase",
    "lowercase.svg": "Lowercase",
    "horizontal_rule.svg": "Trim (whitespace)",
    "find_replace.svg": "Replace",
    "start.svg": "StartsWith",
    "keyboard_tab.svg": "EndsWith",
}

# Logic / Comparison nodes
LOGIC_ICONS = {
    "123.svg": "Number Input",
    "check_box.svg": "Boolean Input",
    "toggle_on.svg": "Boolean Output",
    "drag_handle.svg": "Equal (==)",
    "code.svg": "Not Equal (!=)",
    "chevron_left.svg": "Less Than (<)",
    "keyboard_double_arrow_left.svg": "Less or Equal (<=)",
    "chevron_right.svg": "Greater Than (>)",
    "keyboard_double_arrow_right.svg": "Greater or Equal (>=)",
    "join_inner.svg": "AND (&&)",
    "join_full.svg": "OR (||)",
    "block.svg": "NOT (!)",
    "difference.svg": "XOR (^)",
    "call_split.svg": "If / Switch (?:)",
    "question_mark.svg": "If (alternative)",
}

# Type conversion nodes
CONVERSION_ICONS = {
    "abc.svg": "To String (→str)",
    "123.svg": "To Number (→float)",
    "toggle_on.svg": "To Bool (→bool)",
    "pin.svg": "To Int (→int)",
    "swap_horiz.svg": "Convert (generic)",
    "transform.svg": "Transform (alternative)",
}

# List manipulation nodes
LIST_ICONS = {
    "data_array.svg": "Create List [ ]",
    "filter_1.svg": "Get Item [i]",
    "tag.svg": "List Length #[]",
    "playlist_add.svg": "Append (add to list)",
    "merge.svg": "Join (list → string)",
    "view_list.svg": "List (alternative)",
    "reorder.svg": "Reorder List",
}

# Utility nodes
UTILITY_ICONS = {
    "looks_one.svg": "Constant (C)",
    "print.svg": "Print (console)",
    "comment.svg": "Comment (//)",
    "compress.svg": "Clamp (min/max)",
    "casino.svg": "Random (dice)",
    "tune.svg": "Settings (alternative)",
    "build.svg": "Tool (alternative)",
}

# Time / Date nodes
TIME_ICONS = {
    "schedule.svg": "Current Time (now)",
    "event.svg": "Format Date (→string)",
    "date_range.svg": "Parse Date (string→)",
    "update.svg": "Time Delta (+/-)",
    "compare_arrows.svg": "Compare Time (<>)",
    "alarm.svg": "Alarm (alternative)",
    "calendar_today.svg": "Calendar (alternative)",
    "history.svg": "History (alternative)",
    "av_timer.svg": "Timer (alternative)",
}

# Advanced nodes
ADVANCED_ICONS = {
    "manage_search.svg": "Regex Match (.*)",
    "description.svg": "File Read (load)",
    "save.svg": "File Write (save)",
    "http.svg": "HTTP Request (GET)",
    "cloud_download.svg": "Download (alternative)",
    "cloud_upload.svg": "Upload (alternative)",
    "public.svg": "Web (alternative)",
    "api.svg": "API (alternative)",
}


def load_svg_as_pixmap(svg_path: str, size: int = ICON_SIZE) -> QPixmap:
    """Load an SVG file and convert to QPixmap.

    Args:
        svg_path: Path to the SVG file.
        size: Desired size in pixels.

    Returns:
        QPixmap of the rendered SVG.
    """
    renderer = QSvgRenderer(svg_path)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def create_icon_group(title: str, icons: dict) -> QGroupBox:
    """Create a group box with icons and labels.

    Args:
        title: Title for the group box.
        icons: Dictionary mapping icon filename to description.

    Returns:
        QGroupBox containing the icons.
    """
    group = QGroupBox(title)
    layout = QGridLayout()
    layout.setSpacing(10)

    row = 0
    col = 0
    max_cols = 4

    for icon_name, description in icons.items():
        icon_path = os.path.join(ICONS_SOURCE_PATH, icon_name)

        # Container for icon + label
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(5, 5, 5, 5)
        container_layout.setAlignment(Qt.AlignCenter)

        # Icon label
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(ICON_SIZE + 10, ICON_SIZE + 10)

        if os.path.exists(icon_path):
            pixmap = load_svg_as_pixmap(icon_path)
            icon_label.setPixmap(pixmap)
            icon_label.setStyleSheet("background-color: #2d2d2d; border-radius: 5px;")
        else:
            icon_label.setText("❌")
            icon_label.setStyleSheet("background-color: #ff4444; border-radius: 5px; color: white;")

        # Text labels
        name_label = QLabel(icon_name.replace(".svg", ""))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-weight: bold; font-size: 10px;")

        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 9px; color: #888;")
        desc_label.setFixedWidth(120)

        container_layout.addWidget(icon_label)
        container_layout.addWidget(name_label)
        container_layout.addWidget(desc_label)
        container.setLayout(container_layout)

        layout.addWidget(container, row, col)

        col += 1
        if col >= max_cols:
            col = 0
            row += 1

    group.setLayout(layout)
    return group


class IconViewerWindow(QMainWindow):
    """Main window for displaying icon gallery."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Node Editor Icons - Material Design Selection")
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        # Central widget with scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Main container
        container = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Title
        title = QLabel("Material Design Icons for Node Editor")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Info label
        info = QLabel(f"Source: {ICONS_SOURCE_PATH}")
        info.setStyleSheet("font-size: 11px; color: #666; padding: 5px;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        # Icon groups
        groups = [
            ("🔌 Common (Input/Output)", COMMON_ICONS),
            ("🔢 Calculator / Math", MATH_ICONS),
            ("📝 String Processing", STRING_ICONS),
            ("🔀 Logic / Comparison", LOGIC_ICONS),
            ("🔄 Type Conversion", CONVERSION_ICONS),
            ("📋 List Manipulation", LIST_ICONS),
            ("🛠️ Utility", UTILITY_ICONS),
            ("⏰ Time / Date", TIME_ICONS),
            ("🚀 Advanced", ADVANCED_ICONS),
        ]

        for title, icons in groups:
            group = create_icon_group(title, icons)
            layout.addWidget(group)

        # Summary
        total_icons = sum(len(icons) for _, icons in groups)
        summary = QLabel(f"Total icons selected: {total_icons}")
        summary.setStyleSheet("font-size: 12px; font-weight: bold; padding: 10px;")
        summary.setAlignment(Qt.AlignCenter)
        layout.addWidget(summary)

        # Missing icons check
        missing = []
        for _, icons in groups:
            for icon_name in icons:
                icon_path = os.path.join(ICONS_SOURCE_PATH, icon_name)
                if not os.path.exists(icon_path):
                    missing.append(icon_name)

        if missing:
            missing_label = QLabel(f"⚠️ Missing icons: {', '.join(missing)}")
            missing_label.setStyleSheet("font-size: 11px; color: #ff6600; padding: 5px;")
            missing_label.setWordWrap(True)
            layout.addWidget(missing_label)
        else:
            ok_label = QLabel("✅ All icons found!")
            ok_label.setStyleSheet("font-size: 11px; color: #00cc00; padding: 5px;")
            ok_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(ok_label)

        layout.addStretch()
        container.setLayout(layout)
        scroll.setWidget(container)
        self.setCentralWidget(scroll)


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark theme
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QGroupBox {
            font-weight: bold;
            font-size: 14px;
            border: 1px solid #444;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QScrollArea {
            border: none;
        }
    """)

    window = IconViewerWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
