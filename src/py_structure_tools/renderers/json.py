"""JSON renderer and loader."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import TypeAlias, cast

from py_structure_tools.model import NodeType, TreeNode

JsonValue: TypeAlias = str | int | list["JsonValue"] | dict[str, "JsonValue"] | None
JsonObject: TypeAlias = dict[str, JsonValue]

_NODE_TYPES: frozenset[str] = frozenset({"directory", "file"})


def tree_node_to_dict(node: TreeNode) -> JsonObject:
    """Convert a tree node to a JSON-compatible dictionary.

    Optional metadata keys are only emitted when they are set.
    """
    data: JsonObject = {
        "name": node.name,
        "type": node.type,
    }

    if node.size is not None:
        data["size"] = node.size

    if node.modified is not None:
        data["modified"] = node.modified.isoformat()

    if node.created is not None:
        data["created"] = node.created.isoformat()

    if node.error is not None:
        data["error"] = node.error

    if node.is_dir:
        children: list[JsonValue] = [
            tree_node_to_dict(child) for child in node.children
        ]
        data["children"] = children

    return data


def _require_str(data: dict[str, object], key: str) -> str:
    """Return a mandatory string field or raise."""
    value = data.get(key)

    if not isinstance(value, str):
        msg = f"JSON node field '{key}' must be a string."
        raise TypeError(msg)

    return value


def _optional_str(data: dict[str, object], key: str) -> str | None:
    """Return an optional string field or raise if it has the wrong type."""
    value = data.get(key)

    if value is None:
        return None

    if not isinstance(value, str):
        msg = f"JSON node field '{key}' must be a string."
        raise TypeError(msg)

    return value


def _optional_int(data: dict[str, object], key: str) -> int | None:
    """Return an optional integer field or raise if it has the wrong type."""
    value = data.get(key)

    if value is None:
        return None

    if not isinstance(value, int):
        msg = f"JSON node field '{key}' must be an integer."
        raise TypeError(msg)

    return value


def _optional_datetime(data: dict[str, object], key: str) -> datetime | None:
    """Return an optional ISO-8601 datetime field."""
    raw = _optional_str(data, key)

    return datetime.fromisoformat(raw) if raw is not None else None


def tree_node_from_dict(data: object) -> TreeNode:
    """Rebuild a tree node (and its children) from a parsed JSON object."""
    if not isinstance(data, dict):
        msg = "JSON tree node must be an object."
        raise TypeError(msg)

    mapping = cast("dict[str, object]", data)
    node_type = _require_str(mapping, "type")

    if node_type not in _NODE_TYPES:
        msg = f"Unknown node type in JSON: {node_type!r}."
        raise ValueError(msg)

    raw_children = mapping.get("children", [])

    if not isinstance(raw_children, list):
        msg = "JSON node field 'children' must be a list."
        raise TypeError(msg)

    return TreeNode(
        name=_require_str(mapping, "name"),
        type=cast(NodeType, node_type),
        children=tuple(
            tree_node_from_dict(child) for child in cast("list[object]", raw_children)
        ),
        size=_optional_int(mapping, "size"),
        modified=_optional_datetime(mapping, "modified"),
        created=_optional_datetime(mapping, "created"),
        error=_optional_str(mapping, "error"),
    )


def load_json_tree(path: Path) -> TreeNode:
    """Load a tree previously exported with :func:`export_json`."""
    raw = cast("object", json.loads(path.read_text(encoding="utf-8")))

    return tree_node_from_dict(raw)


def render_json_document(root_node: TreeNode) -> str:
    """Render a complete JSON document."""
    return json.dumps(tree_node_to_dict(root_node), ensure_ascii=False, indent=2) + "\n"


def export_json(root_node: TreeNode, output_path: Path) -> None:
    """Export tree as JSON."""
    _ = output_path.write_text(render_json_document(root_node), encoding="utf-8")
