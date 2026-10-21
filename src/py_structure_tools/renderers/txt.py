"""TXT renderer."""

from __future__ import annotations

from pathlib import Path

from py_structure_tools.model import TreeNode
from py_structure_tools.stats import (
    compute_summary,
    format_node_meta,
    format_summary_lines,
)


def render_txt_lines(node: TreeNode, prefix: str = "") -> list[str]:
    """Render a node as Unicode tree lines (with metadata when available)."""
    lines: list[str] = []

    for index, child in enumerate(node.children):
        is_last = index == len(node.children) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{child.name}{format_node_meta(child)}")

        if child.is_dir:
            extension = "    " if is_last else "│   "
            lines.extend(render_txt_lines(child, prefix + extension))

    return lines


def render_txt_document(root_node: TreeNode, *, show_summary: bool = False) -> str:
    """Render a complete TXT tree document, optionally followed by a summary."""
    lines = [f"{root_node.name}{format_node_meta(root_node)}"]
    lines.extend(render_txt_lines(root_node))

    if show_summary:
        lines.append("")
        lines.extend(format_summary_lines(compute_summary(root_node)))

    return "\n".join(lines) + "\n"


def export_txt(
    root_node: TreeNode,
    output_path: Path,
    *,
    show_summary: bool = False,
) -> None:
    """Export tree as TXT."""
    _ = output_path.write_text(
        render_txt_document(root_node, show_summary=show_summary),
        encoding="utf-8",
    )
