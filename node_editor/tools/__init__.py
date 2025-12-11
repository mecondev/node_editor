"""Tools module for interactive edge manipulation.

This module provides helper classes and validation functions for
interactive edge operations in the node editor:

Classes:
    EdgeDragging: Create new edges by clicking and dragging from sockets.
    EdgeRerouting: Reconnect existing edges to different sockets.
    EdgeIntersect: Insert nodes into edges by dropping them.
    EdgeSnapping: Snap edge endpoints to nearby sockets.

Validator Functions:
    edge_validator_debug: Debug logging validator (always passes).
    edge_cannot_connect_two_outputs_or_two_inputs: Prevent same-type connections.
    edge_cannot_connect_input_and_output_of_same_node: Prevent self-loops.
    edge_cannot_connect_input_and_output_of_different_type: Enforce type matching.

Register validators with Edge.registerEdgeValidator() to enable validation.

Author:
    Michael Economou

Date:
    2025-12-11
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
