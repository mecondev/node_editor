"""
Base Theme - Abstract base class for themes.

All themes should inherit from this class and define their colors.
"""

from PyQt5.QtGui import QColor, QFont


class BaseTheme:
    """Base class for all themes. Subclass this to create new themes."""

    # Theme metadata
    name = "base"
    display_name = "Base Theme"

    # Scene colors
    scene_background = QColor("#393939")
    scene_grid_light = QColor("#2f2f2f")
    scene_grid_dark = QColor("#292929")
    scene_grid_spacing_small = 20
    scene_grid_spacing_large = 100

    # Node colors
    node_background = QColor("#E3212121")
    node_title_background = QColor("#FF313131")
    node_title_color = QColor("#FFFFFF")
    node_border_default = QColor("#7F000000")
    node_border_selected = QColor("#FFFFA637")
    node_border_hovered = QColor("#FF37A6FF")
    node_border_width = 2.0
    node_border_width_hovered = 3.0
    node_border_radius = 10.0
    node_padding = 10

    # Node dimensions
    node_width = 180
    node_height = 240
    node_title_height = 24
    node_title_padding_h = 4.0
    node_title_padding_v = 4.0

    # Edge colors
    edge_color_default = QColor("#001000")
    edge_color_selected = QColor("#00ff00")
    edge_color_dragging = QColor("#FFFFFF")
    edge_width = 3.0
    edge_width_selected = 5.0

    # Socket colors by type
    socket_colors = [
        QColor("#FFFF7700"),  # Type 0 - Orange
        QColor("#FF52e220"),  # Type 1 - Green
        QColor("#FF0056a6"),  # Type 2 - Blue
        QColor("#FFa86db1"),  # Type 3 - Purple
        QColor("#FFb54747"),  # Type 4 - Red
        QColor("#FFdbe220"),  # Type 5 - Yellow
        QColor("#FF888888"),  # Type 6 - Gray
    ]
    socket_radius = 6
    socket_outline_width = 1
    socket_outline_color = QColor("#FF000000")
    socket_highlight_color = QColor("#FF37A6FF")

    # Cutline
    cutline_color = QColor("#FFFF0000")
    cutline_width = 2.0

    # Fonts
    node_title_font = QFont("Ubuntu", 10)
    node_title_font_size = 10

    @classmethod
    def get_socket_color(cls, socket_type: int) -> QColor:
        """Get color for a socket type.
        
        Args:
            socket_type: Socket type index
            
        Returns:
            QColor for the socket type
        """
        if 0 <= socket_type < len(cls.socket_colors):
            return cls.socket_colors[socket_type]
        return cls.socket_colors[0]
