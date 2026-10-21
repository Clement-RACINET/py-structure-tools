"""Local structure generation helpers."""

from __future__ import annotations

import tempfile
from collections.abc import Callable, Iterator
from dataclasses import replace
from pathlib import Path
from typing import Literal, TypeAlias

from py_structure_tools.model import TreeNode

LocalMode: TypeAlias = Literal["init", "all"]
WriteStatus: TypeAlias = Literal["created", "updated", "unchanged"]

LOCAL_MODES: tuple[LocalMode, ...] = ("init", "all")


def has_init_file(node: TreeNode) -> bool:
    """Return whether a directory node directly contains an __init__.py file."""
    return any(child.is_file and child.name == "__init__.py" for child in node.children)


def iter_targets(
    root_node: TreeNode,
    mode: LocalMode,
) -> Iterator[tuple[Path, TreeNode]]:
    """Yield (relative directory, node) for each directory that gets a local file.

    The root is always a target. In "init" mode, a directory is a target only if
    it contains an __init__.py. In "all" mode, every non-empty directory is a target.
    """

    def walk(
        node: TreeNode, relative: Path, is_root: bool
    ) -> Iterator[tuple[Path, TreeNode]]:
        if (
            is_root
            or (mode == "all" and node.children)
            or (mode == "init" and has_init_file(node))
        ):
            yield relative, node

        for child in node.children:
            if child.is_dir:
                yield from walk(child, relative / child.name, is_root=False)

    yield from walk(root_node, Path(), is_root=True)


def limit_depth(
    node: TreeNode,
    max_depth: int | None,
    current_depth: int = 0,
) -> TreeNode:
    """Return a copy of a tree truncated at max_depth (relative to this node)."""
    if node.is_file or max_depth is None:
        return node

    if current_depth >= max_depth:
        return replace(node, children=())

    return replace(
        node,
        children=tuple(
            limit_depth(child, max_depth, current_depth + 1) for child in node.children
        ),
    )


def write_if_changed(
    exporter: Callable[[TreeNode, Path], None],
    node: TreeNode,
    destination: Path,
    *,
    apply: bool,
) -> WriteStatus:
    """Render a node and write it only if the content changed.

    The exporter renders into a temporary directory first, so the result can be
    compared byte by byte with the existing file. Nothing is written if apply is False.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        rendered_path = Path(tmp_dir) / destination.name
        exporter(node, rendered_path)
        new_content = rendered_path.read_bytes()

    if destination.exists():
        if destination.read_bytes() == new_content:
            return "unchanged"
        status: WriteStatus = "updated"
    else:
        status = "created"

    if apply:
        destination.write_bytes(new_content)

    return status
