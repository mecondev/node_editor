#!/bin/bash
# Automated rename of callback methods from camelCase to snake_case
# Phase 1.5 of PEP8 migration plan

set -e  # Exit on error

echo "Starting rename of callback methods..."
echo "Target callbacks:"
echo "  Node callbacks:"
echo "    - onEdgeConnectionChanged → on_edge_connection_changed"
echo "    - onInputChanged → on_input_changed"
echo "    - onDeserialized → on_deserialized"
echo "    - onDoubleClicked → on_double_clicked"
echo "    - onMarkedDirty → on_marked_dirty"
echo "    - onMarkedInvalid → on_marked_invalid"
echo "  Scene callbacks:"
echo "    - onItemSelected → on_item_selected"
echo "    - onItemsDeselected → on_items_deselected"
echo "  Graphics callbacks:"
echo "    - onSelected → on_selected"
echo "  Window callbacks:"
echo "    - onScenePosChanged → on_scene_pos_changed"
echo "    - onFileNew → on_file_new"
echo "    - onFileOpen → on_file_open"
echo "    - onFileSave → on_file_save"
echo "    - onFileSaveAs → on_file_save_as"
echo "    - onBeforeSaveAs → on_before_save_as"
echo "    - onEdit* → on_edit_*"
echo ""

# Apply renames to all Python files in node_editor, tests, and examples
find node_editor tests examples -name "*.py" -type f -exec sed -i \
  -e 's/\.onEdgeConnectionChanged(/.on_edge_connection_changed(/g' \
  -e 's/\.onInputChanged(/.on_input_changed(/g' \
  -e 's/\.onDeserialized(/.on_deserialized(/g' \
  -e 's/\.onDoubleClicked(/.on_double_clicked(/g' \
  -e 's/\.onMarkedDirty(/.on_marked_dirty(/g' \
  -e 's/\.onMarkedInvalid(/.on_marked_invalid(/g' \
  -e 's/\.onItemSelected(/.on_item_selected(/g' \
  -e 's/\.onItemsDeselected(/.on_items_deselected(/g' \
  -e 's/\.onSelected(/.on_selected(/g' \
  -e 's/\.onScenePosChanged(/.on_scene_pos_changed(/g' \
  -e 's/\.onFileNew(/.on_file_new(/g' \
  -e 's/\.onFileOpen(/.on_file_open(/g' \
  -e 's/\.onFileSave(/.on_file_save(/g' \
  -e 's/\.onFileSaveAs(/.on_file_save_as(/g' \
  -e 's/\.onBeforeSaveAs(/.on_before_save_as(/g' \
  -e 's/\.onEditUndo(/.on_edit_undo(/g' \
  -e 's/\.onEditRedo(/.on_edit_redo(/g' \
  -e 's/\.onEditDelete(/.on_edit_delete(/g' \
  -e 's/\.onEditCut(/.on_edit_cut(/g' \
  -e 's/\.onEditCopy(/.on_edit_copy(/g' \
  -e 's/\.onEditPaste(/.on_edit_paste(/g' \
  {} +

echo ""
echo "✓ Rename complete!"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Run tests: pytest"
echo "  3. Run linter: ruff check ."
echo "  4. Test examples manually"
echo "  5. Commit: git commit -m 'Rename callback methods to snake_case (BREAKING)'"
