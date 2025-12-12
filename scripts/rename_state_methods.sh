#!/bin/bash
# Automated rename of state methods from camelCase to snake_case
# Phase 1 of PEP8 migration plan

set -e  # Exit on error

echo "Starting rename of state methods..."
echo "Target methods:"
echo "  - markDirty → mark_dirty"
echo "  - markInvalid → mark_invalid"
echo "  - markDescendantsDirty → mark_descendants_dirty"
echo "  - markDescendantsInvalid → mark_descendants_invalid"
echo ""

# Backup before changes (optional but recommended)
# git stash

# Apply renames to all Python files in node_editor, tests, and examples
find node_editor tests examples -name "*.py" -type f -exec sed -i \
  -e 's/\.markDirty(/.mark_dirty(/g' \
  -e 's/\.markInvalid(/.mark_invalid(/g' \
  -e 's/\.markDescendantsDirty(/.mark_descendants_dirty(/g' \
  -e 's/\.markDescendantsInvalid(/.mark_descendants_invalid(/g' \
  {} +

echo ""
echo "✓ Rename complete!"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Run tests: pytest"
echo "  3. Run linter: ruff check ."
echo "  4. Test examples manually"
echo "  5. Commit: git commit -m 'Rename state methods to snake_case (BREAKING)'"
