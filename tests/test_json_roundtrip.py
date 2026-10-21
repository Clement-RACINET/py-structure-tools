from datetime import UTC, datetime
from pathlib import Path

import pytest

from py_structure_tools.model import TreeNode
from py_structure_tools.renderers.json import export_json, load_json_tree

FILE_SIZE = 42


def test_json_export_then_load_preserves_tree(tmp_path: Path) -> None:
    moment = datetime(2026, 10, 21, 10, 45, tzinfo=UTC)
    tree = TreeNode(
        name="root",
        type="directory",
        children=(
            TreeNode(
                name="a.py",
                type="file",
                size=FILE_SIZE,
                modified=moment,
                created=moment,
            ),
            TreeNode(name="locked", type="directory", error="Permission denied"),
        ),
    )
    target = tmp_path / "structure.json"

    export_json(tree, target)

    assert load_json_tree(target) == tree


@pytest.mark.parametrize(
    "payload",
    [
        "[]",
        "not json at all",
        '{"name": "x", "type": "symlink"}',
        '{"name": 1, "type": "file"}',
        '{"name": "x", "type": "directory", "children": "oops"}',
        '{"name": "x", "type": "file", "size": "big"}',
    ],
)
def test_load_json_tree_rejects_invalid_payload(
    tmp_path: Path,
    payload: str,
) -> None:
    target = tmp_path / "bad.json"
    _ = target.write_text(payload, encoding="utf-8")

    with pytest.raises((TypeError, ValueError)):
        _ = load_json_tree(target)
