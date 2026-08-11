"""JSON renderer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeAlias

from py_structure_tools.model import TreeNode

JsonObject: TypeAlias = dict[str, str | list["JsonObject"]]


def tree_node_to_dict(node: TreeNode) -> JsonObject:
    """Convert a tree node to a JSON-compatible dictionary."""
    data: JsonObject = {
        "name": node.name,
        "type": node.type,
    }

    if node.is_dir:
        data["children"] = [tree_node_to_dict(child) for child in node.children]

    return data


def render_json_document(root_node: TreeNode) -> str:
    """Render a complete JSON document."""
    return json.dumps(tree_node_to_dict(root_node), ensure_ascii=False, indent=2) + "\n"


def export_json(root_node: TreeNode, output_path: Path) -> None:
    """Export tree as JSON."""
    _ = output_path.write_text(render_json_document(root_node), encoding="utf-8")
