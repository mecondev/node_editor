# Stable IDs + Snapshot Refactor Report (2025-12-14)

## Goals (as implemented)

- Replace memory-address identity (`id(self)`) with stable string IDs (ULID).
- Keep core serialization **IO-free** via explicit snapshot APIs.
- Move JSON file read/write into a thin adapter outside `node_editor.core`.
- Add an optional **host/parent bridge** for embedding without Qt/app imports in core.
- Update history and clipboard to operate on stable IDs.

## Stable ID Scheme

- New stable identifier field: `sid: str` (ULID, 26 chars, Crockford base32).
- Backwards compatibility: `id` remains available as a property alias for `sid`.

Implementation:
- ULID generator: [node_editor/utils/ulid.py](../node_editor/utils/ulid.py)
- Serializable base now owns `sid`: [node_editor/core/serializable.py](../node_editor/core/serializable.py)

Notes:
- For *legacy v1 snapshots* (with integer IDs under `"id"`), deserialization does **not** treat legacy ints as stable IDs.
- Instead, legacy IDs are mapped through the `hashmap` during load so references (e.g. edge endpoints) still resolve.

## Snapshot API (core, IO-free)

Scene now provides explicit snapshot APIs:

- `Scene.serialize_snapshot() -> dict`
- `Scene.deserialize_snapshot(data: dict, ...) -> bool`

The existing `Scene.serialize()` / `Scene.deserialize()` methods remain as thin aliases for backward call-site compatibility.

Schema (v2.0.0):

```json
{
  "version": "2.0.0",
  "sid": "01J...ULID...",
  "scene_width": 64000,
  "scene_height": 64000,
  "nodes": [
    {
      "sid": "01J...",
      "title": "Some Node",
      "pos_x": 123.0,
      "pos_y": 456.0,
      "inputs": [{"sid": "01J...", "index": 0, "multi_edges": false, "position": 1, "socket_type": 1}],
      "outputs": [{"sid": "01J...", "index": 0, "multi_edges": true, "position": 4, "socket_type": 1}],
      "content": {}
    }
  ],
  "edges": [
    {
      "sid": "01J...",
      "edge_type": 5,
      "start": "01J...socketSid...",
      "end": "01J...socketSid..."
    }
  ]
}
```

Core serialization changes:
- Nodes: now serialize `"sid"` (not `"id"`).
- Sockets: now serialize `"sid"` (not `"id"`).
- Edges: now serialize `"sid"` and refer to sockets by **socket sid**.

Files:
- [node_editor/core/scene.py](../node_editor/core/scene.py)
- [node_editor/core/node.py](../node_editor/core/node.py)
- [node_editor/core/socket.py](../node_editor/core/socket.py)
- [node_editor/core/edge.py](../node_editor/core/edge.py)

## Persistence Adapter (outside core)

All JSON file IO now lives in:
- [node_editor/persistence/scene_json.py](../node_editor/persistence/scene_json.py)

Provided functions:
- `save_scene_to_file(scene, filename)`
- `load_scene_from_file(scene, filename)`

UI integration was updated accordingly:
- [node_editor/widgets/editor_widget.py](../node_editor/widgets/editor_widget.py)

## History + Clipboard

- History snapshots are stored via `Scene.serialize_snapshot()` and restored via `Scene.deserialize_snapshot()`.
- Selection tracking is now stored/restored using stable `sid` values.
- Clipboard copy/paste uses socket `sid` references and continues to paste with `restore_id=False` semantics (fresh IDs for pasted items).

Files:
- [node_editor/core/history.py](../node_editor/core/history.py)
- [node_editor/core/clipboard.py](../node_editor/core/clipboard.py)

## Host / Parent Data Bridge

A host bridge interface was added so nodes/core can optionally access parent-provided values/services without Qt/app coupling:

- Protocol + no-op default:
  - [node_editor/core/host_bridge.py](../node_editor/core/host_bridge.py)

Scene accepts optional injection:

- `Scene(host_bridge=...)`

and stores:

- `scene.host_bridge`

Default behavior is no-op (`NullNodeHostBridge`).

## Test Updates

All tests were updated to reflect:
- snapshot version `2.0.0`
- stable ID keys (`sid`) in serialized dicts
- file IO via persistence adapter rather than core Scene methods

Test status: `pytest -q` passes.

## Known Compat Notes

- JSON schema changed: `id` keys in snapshots are now `sid`.
- Legacy load support:
  - v1 data is accepted during `deserialize_snapshot` via `hashmap` mapping from legacy integer IDs.
  - No guarantee that v1 IDs remain the same in-memory after load; stable IDs are ULIDs.
