Proposed Improvements and Renaming

The codebase is stable and well-structured. The following small, targeted
improvements will increase clarity and long-term maintainability.

- Rename graphic attributes: `grNode` / `grEdge` / `grSocket` →
  `graphics_node` / `graphics_edge` / `graphics_socket` (PEP8 snake_case).
  This is a public attribute rename and is potentially breaking; provide a
  deprecation shim if adopted.
- Rename state methods: `markDirty` / `markInvalid` → `mark_dirty` /
  `mark_invalid` in `node_editor.core.node` for naming consistency.
  Provide backward-compatible aliases before removal.
- Document `_init_graphics_classes()` clearly as the intentional core→graphics
  bootstrap point to make coupling explicit for contributors.
- Confirm `tools/` is the official location for interactive edge behaviors;
  `edge_tools/` was removed to simplify the public surface.

Migration notes

- For any public rename, add temporary aliases that emit a `DeprecationWarning`.
- Provide a small codemod script (sed/py) to automate renames in downstream code.

I can apply the renames incrementally with deprecation shims if you want me to proceed.