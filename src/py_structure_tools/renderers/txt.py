"""TXT renderer."""

from __future__ import annotations

from pathlib import Path

from py_structure_tools.model import TreeNode


def render_txt_lines(node: TreeNode, prefix: str = "") -> list[str]:
    """Render a node as Unicode tree lines."""
    lines: list[str] = []

    for index, child in enumerate(node.children):
        connector = "└── " if index == len(node.children) - 1 else "├── "
        lines.append(f"{prefix}{connector}{child.name}")

        if child.is_dir:
            extension = "    " if index == len(node.children) - 1 else "│   "
            lines.extend(render_txt_lines(child, prefix + extension))

    return lines


def render_txt_document(root_node: TreeNode) -> str:
    """Render a complete TXT tree document."""
    lines = [root_node.name]
    lines.extend(render_txt_lines(root_node))
    return "\n".join(lines) + "\n"


def export_txt(root_node: TreeNode, output_path: Path) -> None:
    """Export tree as TXT."""
    _ = output_path.write_text(render_txt_document(root_node), encoding="utf-8")
