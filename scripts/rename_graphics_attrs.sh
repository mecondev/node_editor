#!/bin/bash
# Automated rename of graphics attributes from camelCase to snake_case
# Phase 2 of PEP8 migration plan

set -e  # Exit on error

echo "Starting rename of graphics attributes..."
echo "Target attributes:"
echo "  - grNode → graphics_node"
echo "  - grEdge → graphics_edge"
echo "  - grSocket → graphics_socket"
echo "  - grScene → graphics_scene"
echo ""

# Apply renames to all Python files in node_editor, tests, and examples
find node_editor tests examples -name "*.py" -type f -exec sed -i \
  -e 's/\.grNode\b/.graphics_node/g' \
  -e 's/\.grEdge\b/.graphics_edge/g' \
  -e 's/\.grSocket\b/.graphics_socket/g' \
  -e 's/\.grScene\b/.graphics_scene/g' \
  {} +

echo ""
echo "✓ Rename complete!"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Run tests: pytest"
echo "  3. Run linter: ruff check ."
echo "  4. Test examples manually"
echo "  5. Commit: git commit -m 'Rename graphics attributes to snake_case (BREAKING)'"
