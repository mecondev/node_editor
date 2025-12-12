#!/bin/bash
# Phase 3: Rename class attributes to PEP8 snake_case with leading underscore
# GraphicsNode_class -> _graphics_node_class
# GraphicsEdge_class -> _graphics_edge_class

echo "Phase 3: Renaming class attributes..."

find node_editor examples -name "*.py" -type f -exec sed -i \
    -e 's/\bGraphicsNode_class\b/_graphics_node_class/g' \
    -e 's/\bGraphicsEdge_class\b/_graphics_edge_class/g' \
    {} +

echo "Renaming complete. Total changes:"
git diff --stat

echo ""
echo "Run 'pytest' to verify all tests still pass."
