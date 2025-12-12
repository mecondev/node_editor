"""Edge tools placeholder package.

This package was planned to contain edge manipulation tools
per the original refactoring plan (2025-12-10). However, the
decision was made to keep tools in `node_editor/tools/` as
the naming is more generic and allows for future non-edge tools.

See Also:
    node_editor.tools: Active tools package with EdgeDragging,
        EdgeRerouting, EdgeSnapping, EdgeIntersect, and validators.

Note:
    This package exists for backwards compatibility and may be
    removed in a future version. Import from node_editor.tools
    instead.

Author:
    Michael Economou

Date:
    2025-12-12
"""

# Re-export from actual location for backwards compatibility
from node_editor.tools import (
    EdgeDragging,
    EdgeIntersect,
    EdgeRerouting,
    EdgeSnapping,
    edge_cannot_connect_input_and_output_of_different_type,
    edge_cannot_connect_input_and_output_of_same_node,
    edge_cannot_connect_two_outputs_or_two_inputs,
    edge_validator_debug,
)

__all__ = [
    "EdgeDragging",
    "EdgeRerouting",
    "EdgeIntersect",
    "EdgeSnapping",
    "edge_validator_debug",
    "edge_cannot_connect_two_outputs_or_two_inputs",
    "edge_cannot_connect_input_and_output_of_same_node",
    "edge_cannot_connect_input_and_output_of_different_type",
]
