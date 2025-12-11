"""
Tools - Helper tools for edge manipulation.

This module contains various tools for interactive edge manipulation including
dragging, rerouting, snapping, and validation.

Author: Michael Economou
Date: 2025-12-11
"""

from node_editor.tools.edge_dragging import EdgeDragging
from node_editor.tools.edge_intersect import EdgeIntersect
from node_editor.tools.edge_rerouting import EdgeRerouting
from node_editor.tools.edge_snapping import EdgeSnapping
from node_editor.tools.edge_validators import (
    edge_cannot_connect_input_and_output_of_different_type,
    edge_cannot_connect_input_and_output_of_same_node,
    edge_cannot_connect_two_outputs_or_two_inputs,
    edge_validator_debug,
)

__all__ = [
    'EdgeDragging',
    'EdgeRerouting',
    'EdgeIntersect',
    'EdgeSnapping',
    'edge_validator_debug',
    'edge_cannot_connect_two_outputs_or_two_inputs',
    'edge_cannot_connect_input_and_output_of_same_node',
    'edge_cannot_connect_input_and_output_of_different_type',
]
